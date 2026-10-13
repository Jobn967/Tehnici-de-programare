from checker import build_url, is_https, show_response, check_site, scan_sites, check_headers, retry_check

print("Partea 1, build_url", build_url("example.com", "login"))
print("Partea 1, build_url", build_url("example.com", "/login"))
print("Partea 1, is_https", is_https("http://example.com"))
print("Partea 1, is_https", is_https("https://example.com"))

print("Partea: 2\n")
show_response("https://httpbin.org/status/200")
show_response("https://httpbin.org/status/500")

print("Partea 3, check_site", check_site("https://httpbin.org/status/200"))

print("Partea 4\n")
scan_sites()

print("Partea 5, check_headers", check_headers("https://httpbin.org/status/200"))


 
