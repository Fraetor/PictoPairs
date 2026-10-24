# PictoPairs

A drawing game written for [HackNotts '26](https://hacknotts.com/2026/).

## Techstack

* CRDT collaborate drawing.
* Browser canvas API.
* Usable via the internet.
* Client side - ephemral content.
* Basic cloud STUN server.
* Webassembly?

## Gameplay loop

1. Input drawing prompt (Ajective or noun).
2. Paired up with random partner.
3. Given prompt (ajective noun) that contains neither of your prompts.
4. Collaboratively draw until timelimit hit.
5. Vote on favourite drawing.
6. Reset for next round.
