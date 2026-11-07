# Day 13 sources and claim table

All pages opened on 2026-11-07 (web-fetch agents; quotes verbatim, markdown emphasis stripped).

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Proxy_servers_and_tunneling
- https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html
- https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html
- https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html
- https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/
- https://nginx.org/en/docs/http/load_balancing.html
- https://nginx.org/en/docs/http/ngx_http_auth_request_module.html
- https://nginx.org/en/docs/http/ngx_http_limit_req_module.html
- https://nginx.org/en/docs/http/ngx_http_upstream_module.html

| What the video says | Source | Verbatim quote |
|---|---|---|
| In NGINX a reverse proxy uses a location block with proxy_pass (example shape: location, proxy_pass to one server). | https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/ | location /some/path/ { |
| The docs example passes the request with proxy_pass inside a location block. | https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/ | proxy_pass http://www.example.com/link/; |
| proxy_pass passes all requests processed in that location to the proxied server. | https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/ | This example configuration results in passing all requests processed in this location to the proxied server at the specified address. |
| Proxying distributes the load among several servers (reverse proxy and load balancer roles overlap). | https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/ | Proxying is typically used to distribute the load among several servers |
| proxy_pass can point to a named group of servers, so the same directive serves a load balancer. | https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/ | The proxy_pass directive can also be used to pass requests to a named group of servers |
| A reverse proxy can also do load balancing (roles overlap). | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Proxy_servers_and_tunneling | Load balancing: distribute the load to several web servers, |
| Example upstream group of 3 servers: upstream myapp1 { ... } | https://nginx.org/en/docs/http/load_balancing.html | upstream myapp1 { |
| Group member srv1.example.com. | https://nginx.org/en/docs/http/load_balancing.html | server srv1.example.com; |
| Group member srv2.example.com. | https://nginx.org/en/docs/http/load_balancing.html | server srv2.example.com; |
| Group member srv3.example.com. | https://nginx.org/en/docs/http/load_balancing.html | server srv3.example.com; |
| proxy_pass points at the upstream group. | https://nginx.org/en/docs/http/load_balancing.html | proxy_pass http://myapp1; |
| nginx applies HTTP load balancing to the server group. | https://nginx.org/en/docs/http/load_balancing.html | All requests are proxied to the server group myapp1, and nginx applies HTTP load balancing to distribute the requests. |
| With no method configured, it defaults to round-robin. | https://nginx.org/en/docs/http/load_balancing.html | When the load balancing method is not specifically configured, it defaults to round-robin. |
| A failing server is marked failed and nginx tries to avoid it for a while. | https://nginx.org/en/docs/http/load_balancing.html | If the response from a particular server fails with an error, nginx will mark this server as failed, and will try to avoid selecting this server for subsequent inbound requests for a while. |
| max_fails defaults to 1. | https://nginx.org/en/docs/http/ngx_http_upstream_module.html | By default, the number of unsuccessful attempts is set to 1. |
| fail_timeout defaults to 10 seconds. | https://nginx.org/en/docs/http/ngx_http_upstream_module.html | By default, the parameter is set to 10 seconds. |
| fail_timeout is the period the server is considered unavailable. | https://nginx.org/en/docs/http/ngx_http_upstream_module.html | the period of time the server will be considered unavailable. |
| An AWS Application Load Balancer monitors target health and routes only to healthy targets. | https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html | It monitors the health of its registered targets, and routes traffic only to the healthy targets. |
| ALB health check interval defaults to 30 seconds (instance or ip targets). | https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html | The default is 30 seconds if the target type is `instance` or `ip` |
| HealthCheckIntervalSeconds setting name. | https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html | HealthCheckIntervalSeconds |
| UnhealthyThresholdCount setting name. | https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html | UnhealthyThresholdCount |
| ALB unhealthy threshold count defaults to 2. | https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html | The range is 2–10. The default is 2. |
| If a target group contains only unhealthy targets, the load balancer routes requests to all of them. | https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html | If a target group contains only unhealthy registered targets, the load balancer routes requests to all those targets |
| Amazon API Gateway tasks: traffic management, authorization and access control, monitoring, API version management. | https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html | These tasks include traffic management, authorization and access control, monitoring, and API version management. |
| auth_request implements client authorization based on a subrequest. | https://nginx.org/en/docs/http/ngx_http_auth_request_module.html | implements client authorization based on the result of a subrequest. |
| auth_request allows on 2xx. | https://nginx.org/en/docs/http/ngx_http_auth_request_module.html | If the subrequest returns a 2xx response code, the access is allowed. |
| auth_request denies on 401 or 403. | https://nginx.org/en/docs/http/ngx_http_auth_request_module.html | If it returns 401 or 403, the access is denied with the corresponding error code. |
| auth_request /auth; config line. | https://nginx.org/en/docs/http/ngx_http_auth_request_module.html | auth_request /auth; |
| limit_req_zone with rate=1r/s config line. | https://nginx.org/en/docs/http/ngx_http_limit_req_module.html | limit_req_zone $binary_remote_addr zone=one:10m rate=1r/s; |
| limit_req with burst=5 config line. | https://nginx.org/en/docs/http/ngx_http_limit_req_module.html | limit_req zone=one burst=5; |
| Rejected requests get status 503 by default. | https://nginx.org/en/docs/http/ngx_http_limit_req_module.html | Default: limit_req_status 503; |
| limit_req_status sets the status code for rejected requests. | https://nginx.org/en/docs/http/ngx_http_limit_req_module.html | Sets the status code to return in response to rejected requests. |
| Decision rule: load balancer asks which server is healthy (monitors health of targets). | https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html | It monitors the health of its registered targets, and routes traffic only to the healthy targets. |
| Decision rule: API gateway handles authorization and access control. | https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html | These tasks include traffic management, authorization and access control, monitoring, and API version management. |
| Decision rule: reverse proxy sends a path's requests to the proxied server. | https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/ | This example configuration results in passing all requests processed in this location to the proxied server at the specified address. |
| With a single server in a group, max_fails and fail_timeout are ignored (so proxy_pass with 1 server cannot skip a failed one). | https://nginx.org/en/docs/http/ngx_http_upstream_module.html | If there is only a single server in a group, max_fails, fail_timeout and slow_start parameters are ignored, |
| A single server is never considered unavailable. | https://nginx.org/en/docs/http/ngx_http_upstream_module.html | and such a server will never be considered unavailable. |
| max_fails sets the number of unsuccessful attempts to communicate with the server. | https://nginx.org/en/docs/http/ngx_http_upstream_module.html | sets the number of unsuccessful attempts to communicate with the server |
| The attempts are counted in the duration set by fail_timeout. | https://nginx.org/en/docs/http/ngx_http_upstream_module.html | that should happen in the duration set by the fail_timeout parameter |
| ALB health checks run at an interval (approximate time between checks). | https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html | The approximate amount of time, in seconds, between health checks of an individual target. |
| UnhealthyThresholdCount: number of consecutive failed health checks before a target is unhealthy. | https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html | The number of consecutive failed health checks required before considering a target unhealthy. |
| The load balancer routes requests to all unhealthy targets regardless of their health status. | https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html | the load balancer routes requests to all those targets, regardless of their health status. |
| API Gateway handles authorization and access control (what a caller may do). | https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html | These tasks include traffic management, authorization and access control, monitoring, and API version management. |
