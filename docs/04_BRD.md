# Business Requirements Document (BRD)
# VoiceBridge - Real-Time Voice Translation Tool

**Version**: 1.0
**Date**: February 13, 2026
**Based on**: SDP v1.0, UML v1.0, SRS v1.0

---

## 1. Executive Summary

VoiceBridge is a real-time voice translation tool that enables a Korean speaker to participate in English or German video calls by speaking Korean naturally while the other party hears fluent translated speech. The tool addresses the cognitive overhead of real-time mental translation, which degrades a speaker's ability to express complex technical ideas during high-stakes conversations such as job interviews.

---

## 2. Business Problem

### 2.1 Problem Statement
Non-native English speakers face a significant disadvantage in English-language job interviews and professional meetings. The cognitive load of simultaneously thinking in one language and speaking in another reduces the quality of responses, increases hesitation, and limits the complexity of ideas that can be expressed. This is especially acute in technical interviews where nuanced explanations matter.

### 2.2 Quantified Impact
- A native Korean speaker may operate at roughly 60-70% of their full communicative capacity when speaking English in real-time, compared to speaking Korean.
- In a competitive interview scenario, this 30-40% gap can be the difference between demonstrating competence and demonstrating excellence.
- The average tech interview has 4-6 rounds. Each round compounds the fatigue of sustained translation effort.

### 2.3 Current Workarounds
- Practice answers in English beforehand (does not help with unpredictable questions)
- Think slower, speak simpler English (sacrifices depth and nuance)
- Accept the language disadvantage (suboptimal outcome)

---

## 3. Business Objectives

### 3.1 Primary Objective
Enable Heejin to express her full technical depth and strategic thinking during the Anthropic FDE interview on February 19, 2026, by removing the real-time translation bottleneck.

### 3.2 Secondary Objectives
1. **Portfolio demonstration**: The tool itself demonstrates orchestrator-level AI development, directly relevant to the FDE role.
2. **Reusable tool**: Beyond the immediate interview, VoiceBridge can be used for all future English and German professional interactions.
3. **Open-source potential**: If successful, the tool could serve the broader community of non-English-speaking tech professionals.

### 3.3 Alignment with Anthropic's Vision
Dario Amodei's "Machines of Loving Grace" essay envisions AI systems with "text, audio, video, mouse and keyboard control" interfaces. VoiceBridge is a practical implementation of the audio interface dimension -- an AI-powered tool that augments human capability in real-time communication.

Building this tool for the FDE interview demonstrates:
- Understanding of Anthropic's product philosophy
- Ability to identify personal bottlenecks and build AI solutions
- "Level 8" developer proficiency per Steve Yegge's framework (building your own orchestrator)
- Direct, practical experience with the Claude API

---

## 4. Stakeholders

| Stakeholder      | Role                    | Interest                                           |
|------------------|-------------------------|----------------------------------------------------|
| Heejin Jo        | Primary user, developer | Use tool in interview, demonstrate as portfolio     |
| Interview panel  | Indirect user           | Hears translated English output, evaluates Heejin   |
| Anthropic team   | Evaluator               | Evaluates the tool as evidence of FDE capability    |
| Future users     | Potential user base     | Non-English speakers in tech who need this tool     |

---

## 5. Requirements

### 5.1 Business Rules
- **BR-01**: The tool must produce output that sounds natural enough to be mistaken for a non-native but fluent English speaker (not robotic or obviously machine-generated).
- **BR-02**: The delay must be short enough that it feels like a natural conversation pause, not an awkward silence.
- **BR-03**: The tool must not require any interaction from the other party (the interviewer should not need to install or configure anything).
- **BR-04**: The tool must work with standard video conferencing platforms without modification to those platforms.

### 5.2 Success Metrics

| Metric                          | Target              | Measurement Method                    |
|----------------------------------|---------------------|---------------------------------------|
| End-to-end latency              | Under 3 seconds     | Timestamp logging in pipeline         |
| Translation accuracy             | 90%+ meaning preservation | Manual review of 20 test sentences |
| Session stability                | 30+ minutes no crash | Timed test run                       |
| Audio clarity                    | Intelligible to listener | Test call with another person      |
| Setup time for new session       | Under 2 minutes     | Timed from terminal open to ready    |

### 5.3 Budget Constraints

| Service         | Free Tier / Cost                    | Projected Monthly Usage    |
|-----------------|-------------------------------------|----------------------------|
| Deepgram STT    | 12,000 min/year free               | Under 100 min/month        |
| Anthropic Claude| Pay per token (~$0.003/1K tokens)   | Under $5/month             |
| Edge TTS        | Completely free                    | Unlimited                  |
| BlackHole       | Free, open source                  | N/A                        |
| **Total**       |                                     | **Under $5/month**         |

---

## 6. Acceptance Criteria

The project is considered successful when all of the following are demonstrated:

1. Heejin speaks a Korean sentence into her MacBook microphone.
2. Within 3 seconds, the English (or German) translation is spoken through the BlackHole virtual microphone.
3. A Zoom or Google Meet call picks up the translated audio as if Heejin is speaking English.
4. The translation preserves the meaning and tone of the original Korean.
5. The system runs for 30 continuous minutes without manual intervention.
6. The language can be toggled between English and German during a session.

---

## 7. Risks and Mitigations

| Risk                                    | Business Impact                                  | Mitigation                                            |
|-----------------------------------------|--------------------------------------------------|-------------------------------------------------------|
| Tool not ready by Feb 19                | Cannot demonstrate in interview                  | Prioritize core pipeline, cut polish features         |
| Interviewer notices unnatural speech    | Distraction, questions about setup               | Test with multiple TTS voices, optimize for naturalness|
| Latency too high for natural conversation| Awkward pauses hurt interview flow               | Optimize pipeline, pre-warm API connections           |
| Audio feedback loop during call          | Echo or distortion disrupts call                 | Use headphones, test audio routing thoroughly         |
| API outage during interview             | Tool fails at critical moment                    | Have backup plan (speak English directly)             |

---

## 8. Timeline and Milestones

| Date          | Milestone                                | Deliverable                           |
|---------------|------------------------------------------|---------------------------------------|
| Feb 13        | Documentation complete                   | All 6 docs + implementation plan      |
| Feb 14        | Audio capture + STT working              | Korean speech recognized in terminal   |
| Feb 15        | Translation pipeline working             | Korean -> English text in terminal     |
| Feb 16        | TTS + audio output working               | End-to-end audio pipeline functional   |
| Feb 17        | Integration, polish, error handling      | Stable, usable application             |
| Feb 18        | Testing with Zoom, demo preparation      | Verified working in real call scenario |
| Feb 19        | Interview day                            | Tool ready and tested                  |
