# CIFSS: CURL-able Insecure File Storage System

A Simple File storage server that has no regards for security, upload/download without any credintials or "complicated" protocols.



# Endpoints
CIFSS exposes two endpoints:
## /
### `Post` /
Store a file and return a its ID.


### `GET` /`<id>`
Return the file with id=`<id>` in the storage.

---

## /print/
### `GET` /print/`<id>`
Return a dictionary containing information about a file with id=`<id>`.
```json
{
    "id": "{file id: Number}",
    "name": "{file name: String}",
    "mime": "{file mimetype: String}",
    "digest": "{file digest: String}"
}
```
