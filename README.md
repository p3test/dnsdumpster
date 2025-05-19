The script makes a request to DNSDumpster API to get information about a domain (or list of domains), including A, NS, TXT records.
Gets and saves full data in JSON format (example.com.json).

Additionally creates a shortened file (short_example.com.txt) in the format:
```
example.com : 192.0.2.1
doc.example.com : 192.0.2.3
```
## Arguments:
```
Flag Description
-k, --key (required) API key from dnsdumpster.com
-d, --domain One domain to request
-f, --file File with list of domains (one per line)
```

### One domain:
```bash
python3 script.py -k api_key -d example.com
```
### List of domains:
```bash
python3 script.py -k api_key -f domains.txt
```
