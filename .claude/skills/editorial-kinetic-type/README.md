# Example Specs

Reference specs that show the format working. Use as starting templates when drafting new ones.

## mem0-retrieval.json

The original. A teardown of mem0's gated hybrid retrieval algorithm. Demonstrates:

- How to land a technical concept in 8 scenes without diagrams
- The "three things" pattern (Scene 2) for enumerating signals/components
- Accent line placement: scene 3 hits "ships bugs", scene 4 hits "a semantically wrong", scene 6 hits "drop", scene 8 hits "Fuse second"
- The structural inversion between scenes 5 and 7 (scene 5 says "do this," scene 7 says "without this you can't undo X")

## Adapting the format

The 8-scene structure is a teardown template. To adapt it to a different topic:

1. **Title**: name the pattern or concept
2. **Three things**: list the 3 components or signals
3. **Problem**: the failure mode in 2 lines
4. **Specific case**: the concrete instance of that failure in 3 lines
5. **Fix**: 2-word imperative + softer follow-up
6. **Mechanism**: 3 lines explaining HOW the fix works, accent on the punchline
7. **Consequence**: 3 lines on what the fix prevents
8. **Close**: restate the fix + a 1-line builder takeaway

If your topic has more or fewer than 3 components, you can adapt scene 2:
- 2 components: pad with descriptors, or swap to a "before/after" scene structure
- 4+ components: don't. Pick the most important 3. Compression is part of the format.
