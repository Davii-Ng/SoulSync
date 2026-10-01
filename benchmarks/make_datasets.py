"""Regenerates benchmarks/datasets/*.jsonl from the hand-written lists below.

Labels are what a human reader would say about each sentence, NOT what the
engine outputs. Edit the lists here and rerun to change the datasets.
"""

import json
from pathlib import Path

OUT = Path(__file__).parent / "datasets"
OUT.mkdir(exist_ok=True)

rows: list[dict] = []


def add(emotion: str, tag: str, texts: list[str]) -> None:
    for t in texts:
        rows.append({"text": t, "emotion": emotion, "tag": tag})


add("stressed", "plain", [
    "I'm completely exhausted and there is way too much on my plate.",
    "I feel so overwhelmed with deadlines this week.",
    "Work has me drained, I'm running on empty.",
    "I'm burned out and can't function anymore.",
    "I'm drowning in work and have no time to breathe.",
    "Honestly it's been a hectic, long day.",
    "I feel swamped and stretched thin right now.",
    "I'm at my limit, I can't cope with all these exams.",
    "Finals are killing me, I'm falling apart.",
    "There's too much going on and I'm buried in emails.",
    "Kinda stressed about the busy week ahead.",
    "My boss keeps piling on tasks and I'm about to snap.",
])
add("anxious", "plain", [
    "I'm so anxious about tomorrow's interview.",
    "My heart is racing and I can't sleep.",
    "I keep overthinking everything and my mind won't stop.",
    "I feel nervous and on edge all the time.",
    "I had a panic attack on the bus this morning.",
    "I'm worried something bad is going to happen.",
    "There's a knot in my stomach and I feel uneasy.",
    "I'm a little nervous about meeting her parents.",
    "Racing thoughts all night, I just feel restless.",
    "I'm spiraling about what if I fail the test.",
    "Dread hits me every Sunday evening.",
    "My hands are shaking before the presentation.",
])
add("sad", "plain", [
    "I feel so lonely lately.",
    "I've been crying all day and feel empty.",
    "I miss my grandmother so much, the grief is heavy.",
    "I feel numb and depressed.",
    "I'm heartbroken since the breakup.",
    "I feel hopeless and worthless today.",
    "Feeling kinda blue and a little sad today.",
    "I'm devastated, I lost someone close to me.",
    "I feel isolated and forgotten by my friends.",
    "I'm homesick and it's been really hard.",
    "I can't stop crying and I feel broken inside.",
    "Today's just not my best day, feeling down.",
])
add("angry", "plain", [
    "I'm so angry at my roommate right now.",
    "I'm furious, they took credit for my work.",
    "I'm sick of being treated unfairly at work.",
    "That meeting left me pissed and resentful.",
    "I hate how he disrespected me in front of everyone.",
    "I'm fed up with these constant delays.",
    "I was seeing red when I read that email.",
    "I'm livid, I want to scream.",
    "It's infuriating that nobody listens to me.",
    "I feel betrayed and honestly mad at my best friend.",
    "A bit annoyed that the bus was late again.",
    "I feel taken advantage of by my manager.",
])
add("happy", "plain", [
    "I'm so happy, I got the internship!",
    "Today was wonderful and I feel grateful.",
    "I'm over the moon, best day ever!",
    "I'm really proud of what I accomplished this week.",
    "Great news, I'm thrilled and excited!",
    "I feel hopeful and optimistic about the future.",
    "I'm relieved, the results were good news.",
    "Things are looking up and I'm loving life.",
    "Small win today, can't complain.",
    "I had a breakthrough on my project and I'm so proud.",
    "I feel blessed to have such amazing friends.",
    "I'm ecstatic, I made it into the program!",
])
add("calm", "plain", [
    "I feel calm and peaceful this evening.",
    "I'm relaxed and content after my walk.",
    "I feel centered and grounded today.",
    "Everything feels balanced and serene right now.",
    "I'm at ease, just feeling steady.",
    "I'm doing okay, just chilling.",
    "I feel mindful and present during my meditation.",
    "Feeling tranquil, the lake was so quiet.",
    "I'm completely at peace with my decision.",
    "Honestly I'm fine, just hanging in there.",
    "I feel deeply content with how things are.",
    "Today felt peaceful and relaxed.",
])
add("neutral", "neutral", [
    "Hi!", "Hello there.", "Hey, what's up?", "Good morning.",
    "Can you remind me what we talked about?",
    "I went to the store and bought groceries.",
    "I walked the dog and then watched a documentary.",
    "I had a sandwich for lunch.", "The train leaves at noon.",
    "I'm writing in my journal today.", "Just checking in.",
    "I read a chapter of my book.", "Thanks for listening.", "What can you do?",
    "I cleaned my apartment this afternoon.", "Tell me something interesting.",
])

# Negation: the named emotion is explicitly denied.
add("neutral", "negation", [
    "I'm not anxious about the exam at all.",
    "I don't feel nervous anymore.",
    "I'm not worried about it, honestly.",
    "I'm not exhausted and I'm not worried, it was an easy day.",
    "I don't feel depressed, I just had a quiet day.",
    "I'm not frustrated, just tired of typing.",
])
add("calm", "negation", [
    "I'm not angry, I'm just calm about it.",
    "I'm not sad anymore, I feel peaceful.",
    "I'm not stressed, I feel relaxed today.",
    "I wasn't angry at all, I'm just fine.",
    "I'm not nervous or on edge, everything is fine.",
])
add("happy", "negation", [
    "I never felt lonely, my friends are great and I'm happy.",
    "I'm not overwhelmed, I feel proud of how I handled it.",
])

MIXED = [
    ("I'm anxious about the move but excited for the new job.", "anxious", "happy"),
    ("I feel sad and lonely, and I'm also angry at myself.", "sad", "angry"),
    ("I'm exhausted and overwhelmed, and a bit worried about money.", "stressed", "anxious"),
    ("I'm furious and honestly heartbroken about what happened.", "angry", "sad"),
    ("I'm grateful and proud but also nervous about what's next.", "happy", "anxious"),
    ("I feel relieved and happy, though still kind of tired and drained.", "happy", "stressed"),
    ("I'm worried and overthinking, and lonely too.", "anxious", "sad"),
    ("I'm frustrated and fed up, totally overwhelmed with this project.", "angry", "stressed"),
    ("I feel calm and content, and a little grateful.", "calm", "happy"),
    ("I'm depressed and numb, and anxious about tomorrow.", "sad", "anxious"),
]
for text, primary, secondary in MIXED:
    rows.append({"text": text, "emotion": primary, "secondary": secondary, "tag": "mixed"})

CRISIS = [
    "I want to die.", "I just want to end it all.", "I've been thinking about killing myself.",
    "I feel like I should hurt myself.", "I don't want to be here anymore.",
    "There's no reason to live.", "Honestly I'm better off dead.",
    "I've been researching suicide methods.", "I started to self-harm again last night.",
    "I cut myself again after work.", "I wish I was dead.", "I wish I wasn't alive.",
    "I can't go on like this.", "This is my goodbye forever.", "I wrote a final note.",
    "I'm planning to jump off the bridge.", "I thought about taking all the pills in the cabinet.",
    "I'm done, I'm going to end my life tonight.", "I keep thinking I should just overdose.",
    "I think about hanging myself every night.", "I want to slit my wrist.",
    "What's the point, and honestly no one would miss me.",
    "I'm a burden and everyone would be better off without me.",
    "I don't see a future and I have nothing left for me.",
    "I can't take it anymore, I give up on everything.",
    "I feel hopeless and worthless and what's the point of any of it.",
    "I'm too tired to keep trying, I'm a burden to everyone.",
    "Lately I just want to disappear and there's nothing left for me here.",
    "I'm not gonna be around much longer.",
    "Nobody would care if I disappeared for good.",
]

# Intense or idiomatic, but NOT a crisis. Hard negatives for keyword matchers.
BENIGN = [
    ("This deadline is killing me.", "stressed"),
    ("I could die of embarrassment after that presentation.", "anxious"),
    ("That joke killed me, I was dying of laughter.", "happy"),
    ("I'm dying to see the new movie, so excited!", "happy"),
    ("My phone battery is dead and I'm mad.", "angry"),
    ("I drank an overdose of caffeine, now I'm jittery and nervous.", "anxious"),
    ("I want to disappear into a book this weekend and relax.", "calm"),
    ("I'm exhausted and overwhelmed, honestly drained.", "stressed"),
    ("I feel really sad and lonely tonight.", "sad"),
    ("I'm furious at my landlord.", "angry"),
    ("I have a panic attack coming whenever I think of the exam.", "anxious"),
    ("My boss is a pain, I hate this job.", "angry"),
    ("We watched a documentary about suicide prevention awareness for class.", "neutral"),
    ("I'm reading a novel where the main character jumps off a cliff in the final scene.", "neutral"),
    ("I'm writing a paper on self-harm statistics for my psychology class.", "neutral"),
    ("The doctor said never to overdose on vitamins, so I read the label.", "neutral"),
    ("I feel hopeless about my team's chances this season, but whatever.", "sad"),
    ("I give up on this crossword, it's too hard.", "stressed"),
    ("I can't take it anymore, this construction noise is so annoying.", "angry"),
    ("What's the point of arguing with the thermostat?", "neutral"),
    ("I'm a burden on the printer today, it keeps jamming, ugh.", "angry"),
    ("I miss someone and feel lonely tonight.", "sad"),
    ("I had a tough day but I'm okay.", "neutral"),
    ("I'm stressed, tired, and a bit sad but I'm safe and talking to friends.", "stressed"),
    ("Our cat knocked everything off the shelf and I could scream.", "angry"),
    ("It's okay, I'm just really down today.", "sad"),
    ("I'm anxious about flying but I'm managing.", "anxious"),
    ("Today I felt worthless at the gym, I couldn't lift anything.", "sad"),
    ("I'm too tired to keep trying to learn this guitar riff.", "stressed"),
    ("My job feels like a dead end but I'm updating my resume.", "stressed"),
    ("I'm cutting myself some slack this week.", "calm"),
    ("That show had me killing myself laughing.", "happy"),
    ("I'm ending my lifelong habit of procrastinating.", "neutral"),
]

# Calendar intent. has_event = a human would say a schedulable event is present.
EVENTS = [
    ("I have a dentist appointment on Friday at 3pm.", True, "dentist", "15:00"),
    ("Remind me about the team meeting tomorrow at 10am.", True, "team meeting", "10:00"),
    ("My project deadline is next Monday.", True, "project deadline", ""),
    ("Interview with Google on 4/15 at 2pm.", True, "interview", "14:00"),
    ("I have a therapy session Wednesday at 5:30 pm.", True, "therapy", "17:30"),
    ("Don't let me forget my sister's birthday dinner on Saturday.", True, "birthday dinner", ""),
    ("Doctor's appointment next Tuesday at 9am.", True, "doctor", "09:00"),
    ("Final exam on 12/10.", True, "final exam", ""),
    ("Coffee with Maya tomorrow at 8am.", True, "coffee", "08:00"),
    ("I need to submit my application by Thursday.", True, "application", ""),
    ("Gym class at 6pm on Monday.", True, "gym", "18:00"),
    ("Remind me to call mom on Sunday.", True, "call mom", ""),
    ("Group project meeting on Friday at 1pm.", True, "group project meeting", "13:00"),
    ("Flight to Tampa next Thursday at 7am.", True, "flight", "07:00"),
    ("Hair appointment at 4pm tomorrow.", True, "hair appointment", "16:00"),
    ("Midterm review session on Wednesday.", True, "midterm review", ""),
    ("I have a meeting at 3pm today.", True, "meeting", "15:00"),
    ("Lunch with my advisor on Tuesday at noon.", True, "lunch", "12:00"),
    ("Pay rent deadline on the 1st, remind me.", True, "rent", ""),
    ("Dinner reservation Saturday at 7pm.", True, "dinner", "19:00"),
    ("I feel really anxious about everything.", False, "", ""),
    ("I'm so happy today.", False, "", ""),
    ("I felt stressed yesterday.", False, "", ""),
    ("My day was long and tiring.", False, "", ""),
    ("I'm sad about what happened last week.", False, "", ""),
    ("I think I want to be more mindful.", False, "", ""),
    ("Thanks for listening to me.", False, "", ""),
    ("I'm tired of the way things are going.", False, "", ""),
    ("I miss my friends back home.", False, "", ""),
    ("I'm proud of myself.", False, "", ""),
    ("I think tomorrow will be better.", False, "", ""),
    ("Tomorrow I just want to relax and not think.", False, "", ""),
    ("I hope Friday feels lighter than this week did.", False, "", ""),
    ("I was so nervous on Monday and cried a bit.", False, "", ""),
    ("Sunday was a good day, I felt calm.", False, "", ""),
    ("I'm worried the next day will be worse.", False, "", ""),
    ("I keep thinking about last Tuesday.", False, "", ""),
    ("I'll feel better at some point.", False, "", ""),
    ("It's been a hectic week.", False, "", ""),
    ("I feel hopeful about next year.", False, "", ""),
]


def dump(name: str, items: list[dict]) -> None:
    with open(OUT / name, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"{name}: {len(items)}")


dump("emotion_labeled.jsonl", rows)
dump("crisis.jsonl", [{"text": t} for t in CRISIS])
dump("benign.jsonl", [{"text": t, "emotion": e} for t, e in BENIGN])
dump("events.jsonl", [
    {"text": t, "has_event": h, "title_contains": title, "time": tm}
    for t, h, title, tm in EVENTS
])
