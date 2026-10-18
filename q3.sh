out=$(uv run --with httpie -- http --json POST https://httpbin.org/post email=23f2003826@ds.study.iitm.ac.in request_id=67163d40)
echo "$out"
