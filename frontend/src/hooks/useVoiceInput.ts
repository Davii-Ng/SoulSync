// Web Speech API hook for voice-to-text

import { useState, useRef, useCallback } from "react";

interface UseVoiceInputReturn {
  isListening: boolean;
  transcript: string;
  startListening: (onResult: (text: string) => void) => void;
  stopListening: () => Promise<string>;
}

export function useVoiceInput(): UseVoiceInputReturn {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const callbackRef = useRef<((text: string) => void) | null>(null);
  const latestTranscriptRef = useRef("");

  const startListening = useCallback((onResult: (text: string) => void) => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.error("Speech Recognition not supported");
      return;
    }

    callbackRef.current = onResult;
    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = true;
    recognition.continuous = true;

    recognition.onresult = (event) => {
      // Concat all results (continuous mode produces multiple)
      let text = "";
      for (let i = 0; i < event.results.length; i++) {
        text += event.results[i][0].transcript;
      }
      latestTranscriptRef.current = text;
      setTranscript(text);
    };

    recognition.onend = () => {
      setIsListening(false);
      // If stopped via stopListening(), the promise handler takes over
      // If ended naturally (e.g. silence timeout), fire the callback
      if (callbackRef.current && latestTranscriptRef.current) {
        callbackRef.current(latestTranscriptRef.current);
        callbackRef.current = null;
      }
    };
    recognition.addEventListener("error", (event) => {
      // event.error: "not-allowed" | "no-speech" | "network" | "aborted" etc.
      const reason = (event as unknown as { error: string }).error ?? "unknown";
      console.error("Speech recognition error:", reason);
      // "no-speech" fires when silence is detected — not a real failure,
      // the recognition keeps running in continuous mode
      if (reason === "no-speech") return;
      setIsListening(false);
      callbackRef.current = null;
    });

    recognitionRef.current = recognition;
    latestTranscriptRef.current = "";
    setTranscript("");
    recognition.start();
    setIsListening(true);
  }, []);

  const stopListening = useCallback((): Promise<string> => {
    return new Promise((resolve) => {
      const recognition = recognitionRef.current;
      if (!recognition) {
        setIsListening(false);
        resolve("");
        return;
      }

      let settled = false;
      const finish = () => {
        if (settled) return;
        settled = true;
        setIsListening(false);
        recognitionRef.current = null;
        const text = latestTranscriptRef.current;
        if (savedCallback && text) {
          savedCallback(text);
        }
        resolve(text);
      };

      const savedCallback = callbackRef.current;
      callbackRef.current = null;

      recognition.onend = finish;
      recognition.onerror = finish;

      // Safety timeout — if onend never fires, force cleanup
      setTimeout(finish, 500);

      try {
        recognition.stop();
      } catch {
        finish();
      }
    });
  }, []);

  return { isListening, transcript, startListening, stopListening };
}
