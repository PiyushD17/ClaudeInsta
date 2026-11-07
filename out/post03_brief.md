# Brief: P03 cache stampede (carousel, 7 slides)
Experiment tag: FAILURE (a relatable production failure; secondary angle COUNTER: a cache can overload the thing it protects).

## 1. Topic and audience
What happens when many requests miss the same expired cache entry (cache stampede / thundering herd) and the three defences: lock, serve stale, recompute before expiry, each with its cost. Audience: backend and platform engineers who run caches. Value outcome: "I did not know that" (nginx's cache lock is off by default and gives up after 5 seconds) and "I should save this" (recap of defences and costs).

## 2. Cover headlines (hookscore.py)
1. 81.4 "1 expired cache entry can still flood your database" (recommended: number, true thanks to "can", speaks to the reader)
2. 80.0 "But 1 expired entry can flood the database your cache protects"
3. 77.8 "Your cache can fail your database when 1 entry expires"
Rejected despite 81.4: "Without 1 lock, your cache can crash your database" (overstated), "When 1 cache entry expires, your database is not protected" (false when a lock or stale copy is used).

## 3. Storyboard (exact slide text is in out/post03_s01.png to s07.png and specs/post03_cache_stampede.py)
1 Cover (L1): headline, tags CACHING, SYSTEM DESIGN, NO CODE. Purpose: promise the failure.
2 STEP 01 "A cache shields your database" (L1): why caches exist, TTL, cache miss. Rehook 75.7: what happens to your database when many requests arrive?
3 STEP 02 "Everyone misses together" (L1): cache stampede, thundering herd, overload, congestion collapse. Rehook 78.6: how can only 1 request rebuild?
4 STEP 03 "One request rebuilds while the rest wait" (L2): lock; nginx cache lock, off by default, 5 s wait then request goes through uncached. This is the send-or-save slide. Rehook 85.6: must anyone wait?
5 STEP 04 "Serve the stale copy" (L3): stale item, nginx stale-while-updating and background update (both opt-in), stale data versus errors. Rehook 85.6: refresh before expiry?
6 STEP 05 "Refresh before it expires" (L3): probabilistic early expiration, rebuild time scales the chance, beta of 1, extra memory cost. Rehook 63.8: defences and costs on 1 slide.
7 Recap (L3): three defences with a cost each; share line "Send this to whoever runs your cache. nginx's lock is off by default." Follow line drawn automatically.
Visual treatment: plain dark background, amber accent word per title, no code, no background numerals; mascot on cover and recap only.

## 4. Accuracy caveats
- The nginx lock, stale serving and background update are nginx behaviours and all default off; other caches differ. The post says "nginx" wherever it is nginx-specific.
- A stampede "can" overload a database; it needs a high request rate and an expensive rebuild. Not every expiry causes one.
- Lock timeout: after 5 s by default a waiting request is passed to the proxied server and its response is not cached, so a stampede can still happen after the wait.
- "The longer a rebuild takes, the earlier requests may start it" is a reading of the published formula (delta scales the probability), not a sentence from the source. The XFetch paper itself was not opened; Wikipedia states the authors show beta of 1 works well in practice.
- Wikipedia and AWS quotes are excerpts of 125 characters at most because of the fetch tool.

## 5. Thumbnail headline (3-7 words)
"1 expired entry can flood your database" (6 words)

## 6. Caption
See out/post03_caption.txt.

## 7. Audio
Not applicable (carousel).

## 8. Performance hypothesis
Against the baseline of about 150 views per reel (carousels are a different format, so no direct comparison is valid): a concrete failure cover plus a recap that lists each defence with its cost should be saved by engineers. Validating metric: saves per 100 views (and sends per 100 views). No target is forecast; there are 0 filled post rows yet.

## 9. Experiment tag
FAILURE.
