export function ResourcesPage() {
  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-2xl section-heading text-soul-text">
          Resources
        </h1>
        <p className="text-sm mt-1 text-soul-text-muted">
          Support is always available. You are not alone.
        </p>
      </div>

      {/* Crisis Resources */}
      <div className="dashboard-card rounded-2xl border border-soul-border-light p-5 md:p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="material-symbols-outlined text-lg text-soul-error">
            emergency
          </span>
          <h2 className="text-base font-semibold text-soul-text">
            Crisis Support
          </h2>
        </div>
        <div className="flex flex-col gap-3">
          {[
            {
              name: '988 Suicide & Crisis Lifeline',
              action: 'Call or text 988',
              description: 'Free, confidential support 24/7 for people in distress.',
              icon: 'call',
              highlight: true,
            },
            {
              name: 'Crisis Text Line',
              action: 'Text HOME to 741741',
              description: 'Free crisis counseling via text message, available 24/7.',
              icon: 'sms',
              highlight: true,
            },
            {
              name: 'National Domestic Violence Hotline',
              action: 'Call 1-800-799-7233',
              description: 'Confidential support for domestic violence situations.',
              icon: 'shield',
              highlight: false,
            },
            {
              name: 'SAMHSA National Helpline',
              action: 'Call 1-800-662-4357',
              description: 'Free referrals and information for mental health and substance use.',
              icon: 'support_agent',
              highlight: false,
            },
          ].map((resource) => (
            <div
              key={resource.name}
              className={`rounded-xl p-4 flex items-start gap-3 resource-row cursor-pointer border ${
                resource.highlight
                  ? 'bg-soul-accent-pale border-soul-accent-light'
                  : 'bg-soul-surface-alt border-soul-border-light'
              }`}
            >
              <div
                className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                  resource.highlight ? 'bg-soul-accent' : 'bg-soul-border-light'
                }`}
              >
                <span className="material-symbols-outlined text-lg text-white">
                  {resource.icon}
                </span>
              </div>
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-soul-text">
                  {resource.name}
                </h3>
                <p className="text-xs font-semibold mt-0.5 text-soul-accent">
                  {resource.action}
                </p>
                <p className="text-xs mt-1 text-soul-text-muted">
                  {resource.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Therapy & Counseling */}
      <div className="dashboard-card rounded-2xl border border-soul-border-light p-5 md:p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="material-symbols-outlined text-lg text-soul-accent">
            psychology
          </span>
          <h2 className="text-base font-semibold text-soul-text">
            Therapy & Counseling
          </h2>
        </div>
        <div className="flex flex-col gap-3">
          {[
            {
              name: 'Psychology Today - Find a Therapist',
              description: 'Search therapists by location, specialty, and insurance.',
              icon: 'search',
            },
            {
              name: 'Open Path Collective',
              description: 'Affordable therapy sessions ($30-$80) with licensed providers.',
              icon: 'volunteer_activism',
            },
            {
              name: 'BetterHelp / Talkspace',
              description: 'Online therapy platforms with licensed counselors.',
              icon: 'laptop',
            },
          ].map((resource) => (
            <div
              key={resource.name}
              className="rounded-xl p-4 flex items-start gap-3 resource-row cursor-pointer bg-soul-surface-alt border border-soul-border-light"
            >
              <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 bg-soul-accent-pale">
                <span className="material-symbols-outlined text-lg text-soul-accent">
                  {resource.icon}
                </span>
              </div>
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-soul-text">
                  {resource.name}
                </h3>
                <p className="text-xs mt-1 text-soul-text-muted">
                  {resource.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Mindfulness & Coping */}
      <div className="dashboard-card rounded-2xl border border-soul-border-light p-5 md:p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="material-symbols-outlined text-lg text-soul-accent">
            self_improvement
          </span>
          <h2 className="text-base font-semibold text-soul-text">
            Mindfulness & Coping
          </h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {[
            {
              name: 'Box Breathing',
              description: 'Inhale 4s, hold 4s, exhale 4s, hold 4s. Repeat 4 times.',
              icon: 'air',
            },
            {
              name: '5-4-3-2-1 Grounding',
              description: 'Name 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste.',
              icon: 'spa',
            },
            {
              name: 'Progressive Muscle Relaxation',
              description: 'Tense and release each muscle group for 5-10 seconds.',
              icon: 'fitness_center',
            },
            {
              name: 'Mindful Journaling',
              description: 'Write freely for 5 minutes about how you feel right now.',
              icon: 'edit_note',
            },
          ].map((exercise) => (
            <div
              key={exercise.name}
              className="rounded-xl p-4 resource-row cursor-pointer bg-soul-surface-alt border border-soul-border-light"
            >
              <span className="material-symbols-outlined text-2xl mb-2 block text-soul-accent">
                {exercise.icon}
              </span>
              <h3 className="text-sm font-semibold text-soul-text">
                {exercise.name}
              </h3>
              <p className="text-xs mt-1 text-soul-text-muted">
                {exercise.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
