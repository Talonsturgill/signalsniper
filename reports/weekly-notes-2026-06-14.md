# Substack Notes — Issue 7 · ready to post

## Note 1 (Sunday at publication, or 1 hour after)
Five repos climbed this week and none of them shipped a new model. @a1zhang, @ChengYihuaA and @SteveSolun all won by deciding what their model never has to look at. Full ranking, including the one that beat a far bigger model by 34 points.
<SUBSTACK_POST_URL>

## Note 2 (Monday morning)
RLM hides recursion behind a single call. The root model writes code that breaks a long input into pieces and answers each, so a small model can punch above a far bigger one. @a1zhang built it in the open and strangers ported it before he asked.
https://x.com/a1zhang

## Note 3 (Tuesday)
Counter-programming the week. While most of the field races to bolt more skills onto agents, @SteveSolun's ctx ranks tens of thousands of them and hands back only the dozen that fit the job. Subtraction shipped as a feature.

## Note 4 (Thursday)
Most stacks recompute the attention cache on every request and eat the GPU bill for it. @ChengYihuaA's LMCache keeps that cache and shares it across serving engines, which is why the ecosystem is quietly standardizing on it. Past 9,400 stars.
https://x.com/ChengYihuaA

## Note 5 (Saturday, tee up next issue)
Watching next week. Whether @ollama's MLX gains plus Apple's fresh speculative decoding pull more local inference onto the draft-model path, and any sign Recursive Language Models cross from blog posts into a product people pay for.
