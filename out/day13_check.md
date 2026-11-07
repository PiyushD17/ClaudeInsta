# Check report
- INFO LENGTH_LONG: Script has 338 words (about 110 s). Finish rate falls with length: aim for 35 to 45 s (about 105 to 135 words) and cut anything that does not move the story.

Result: 0 FAIL, 0 WARN. Reviewer pass still required.
## Script next to on-screen text (reviewer reads this)

### Scene 1 [stage] 0.0-4.4s
SAID : Your 1 proxy_pass can be a reverse proxy, but also a load balancer.
SHOWN [object]: TECH IN A BITE
SHOWN [headline]: Your 1 proxy_pass:
reverse proxy or load balancer
SHOWN [headline]: NGINX · reverse proxy · load balancer
SHOWN [object]: alice
SHOWN [object]: Example
SHOWN [object]: NGINX
SHOWN [object]: Reverse proxy
SHOWN [object]: proxy_pass
SHOWN [object]: Load balancer
SHOWN [object]: proxy_pass
SHOWN [object]: API gateway
SHOWN [object]: auth_request
SHOWN [object]: Servers
SHOWN [object]: srv1
SHOWN [object]: GET

### Scene 2 [stage] 4.4-16.3s
SAID : Three jobs can sit in front of your servers: a reverse proxy, a load balancer and an API gateway. In our example, alice calls GET /orders/42 through NGINX, and each job asks that request a different question.
SHOWN [object]: Reverse proxy
SHOWN [object]: Load balancer
SHOWN [object]: API gateway
SHOWN [headline]: Same request, 3 questions
SHOWN [object]: /orders/42
SHOWN [object]: GET

### Scene 3 [stage] 16.3-28.9s
SAID : The reverse proxy asks which server handles this path of the request. In NGINX, a location block with proxy_pass, as in the docs example, passes all requests processed in that location to the proxied server at the specified address.
SHOWN [headline]: Reverse proxy: which server?
SHOWN [object]: GET
SHOWN [object]: GET
SHOWN [object]: Example: NGINX config
SHOWN [code]: location /orders/ {
SHOWN [code]:     proxy_pass http://srv1.example.com;
SHOWN [code]: }

### Scene 4 [stage] 28.9-34.6s
SAID : If srv1 fails, your 1-server proxy_pass has no other server to try. What do 3 servers add?
SHOWN [headline]: Failed server. What do 3 servers add?
SHOWN [object]: proxy_pass: 1 SERVER
SHOWN [object]: srv1 FAILED

### Scene 5 [stage] 34.6-42.5s
SAID : Point proxy_pass at an upstream group with 3 servers, srv1, srv2 and srv3, and nginx applies HTTP load balancing. The default method is round-robin.
SHOWN [headline]: Load balancer: upstream group
SHOWN [object]: srv2
SHOWN [object]: srv3
SHOWN [object]: GET
SHOWN [object]: GET
SHOWN [object]: GET
SHOWN [object]: NGINX docs: default load balancing configuration
SHOWN [code]: upstream myapp1 {
SHOWN [code]:     server srv1.example.com;
SHOWN [code]:     server srv2.example.com;
SHOWN [code]:     server srv3.example.com;
SHOWN [code]: }
SHOWN [code]: proxy_pass http://myapp1;
SHOWN [code]: -- default method: round-robin

### Scene 6 [stage] 42.5-53.6s
SAID : What the group adds is skipping: when a response from a server fails, nginx marks it unavailable and tries to avoid it for a while. max_fails defaults to 1 and fail_timeout to 10 seconds.
SHOWN [headline]: Group: skips failed servers
SHOWN [object]: GET
SHOWN [object]: GET
SHOWN [object]: NGINX docs: server parameters
SHOWN [code]: -> srv1 marked unavailable
SHOWN [code]: -> tries to avoid it for a while
SHOWN [code]: max_fails=1        -- default
SHOWN [code]: fail_timeout=10s   -- default

### Scene 7 [stage] 53.6-63.3s
SAID : An AWS Application Load Balancer sends its own health checks: about every 30 seconds by default for instance and IP targets, and by default 2 consecutive failed checks mean unhealthy.
SHOWN [headline]: AWS load balancer: health checks
SHOWN [object]: AWS docs: health check defaults
SHOWN [code]: Application Load Balancer
SHOWN [code]: HealthCheckIntervalSeconds  30
SHOWN [code]: UnhealthyThresholdCount     2
SHOWN [code]: -- defaults; 2 consecutive failed checks
SHOWN [object]: ALB targets

### Scene 8 [stage] 63.3-70.6s
SAID : The catch: if a target group contains only unhealthy targets, the load balancer routes requests to all of them, regardless of health.
SHOWN [headline]: Catch: only unhealthy targets
SHOWN [object]: Example: 3 AWS targets
SHOWN [code]: healthy targets:   0 of 3
SHOWN [code]: -> requests go to ALL targets
SHOWN [code]: -- regardless of health

### Scene 9 [stage] 70.6-78.8s
SAID : The API gateway asks who is calling and what they may do. Amazon API Gateway lists traffic management, authorization and access control among its tasks.
SHOWN [headline]: API gateway: who may call?
SHOWN [object]: AWS docs: what API Gateway handles
SHOWN [code]: traffic management
SHOWN [code]: authorization and access control
SHOWN [object]: Servers

### Scene 10 [stage] 78.8-89.8s
SAID : NGINX has directives for such tasks too: auth_request allows alice on a 2xx subrequest and denies on 401 or 403, and limit_req_zone sets a rate of 1r/s, and rejected requests get 503 by default.
SHOWN [headline]: NGINX: auth_request, limit_req
SHOWN [object]: GET
SHOWN [object]: 401
SHOWN [object]: 503
SHOWN [object]: NGINX docs: access and rate limits
SHOWN [code]: auth_request /auth;
SHOWN [code]: -- 2xx: allowed, 401 or 403: denied
SHOWN [code]: limit_req_zone $binary_remote_addr zone=one:10m rate=1r/s;
SHOWN [code]: limit_req zone=one burst=5;
SHOWN [code]: -- rejected requests: status 503 (default)

### Scene 11 [stage] 89.8-99.6s
SAID : Save this rule of thumb, since roles overlap: usually, the load balancer answers which server is healthy, the gateway who is calling, and the reverse proxy which path goes where.
SHOWN [headline]: Which question, which job?
SHOWN [object]: Which server is healthy?
SHOWN [object]: Load balancer
SHOWN [object]: Who is calling?
SHOWN [object]: API gateway
SHOWN [object]: Which path goes where?
SHOWN [object]: Reverse proxy

### Scene 12 [stage] 99.6-111.7s
SAID : So proxy_pass at 1 server is a plain reverse proxy; at an upstream group of 3 it also load balances. The gateway adds who is calling. Follow for one tech topic a day.
SHOWN [object]: Reverse proxy
SHOWN [object]: Load balancer
SHOWN [object]: API gateway
SHOWN [headline]: proxy_pass: 2 jobs, plus the gateway
SHOWN [object]: @techinabite
SHOWN [headline]: Follow for one tech topic a day.
