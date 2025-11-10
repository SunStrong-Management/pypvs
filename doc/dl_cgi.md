# Legacy DL-CGI methods that are still supported 

Those methods could be called using the legacy dl_cgi interface on the gateways,
using HTTP or HTTPS interface, but they are not recommended for any API like usage
and could change without further notice.
The method that require authentication needs to be called same way as described in [LocalAPI](LocalAPI.md).

# PVS5 Gateway

## Open

```http
  GET /communication/interfaces
  GET /supervisor/info
```

## Requiring authentication

```http
  GET /network/powerProduction
  GET /network/interfaces
  GET /communication/interfaces
  GET /devices/list
  GET /supervisor/info
```

# PVS6 Gateway

## Open

```http
  GET /communication/interfaces
  GET /supervisor/info
```

## Requiring authentication

```http
  GET /network/powerProduction
  GET /network/interfaces
  GET /communication/interfaces
  GET /devices/list
  GET /supervisor/info
```
