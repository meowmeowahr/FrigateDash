<p align="center">
  <img align="center" alt="FrigateDash" src="docs/logo.png" width=192>
</p>

# FrigateDash — A dashboard for RTSP Cameras
Despite the name, Frigate is not currently required to use this dashboard, but may be in the future.

NOTE: Non-RTSP cameras may work, but are not currently supported.

### Recomended Hardware
* Raspberry Pi 3B or greater
* [Generic 3.5in Touchscreen](https://www.amazon.com/gp/product/B00OZLG2YS/)
* [6x6x9 Tactile Buttons](https://www.amazon.com/gp/product/B06VY1WJ8Z/)

## Settings File
A `settings.json` file must be created inside the program directory before launching the program

### Example file for Amcrest IP Cameras
```
{
  "views": [
    {
      "stream":  "rtsp://admin:PASSWORD@192.168.1.23:554/cam/realmonitor?channel=1&subtype=0",
      "name":  "Patio Camera"
    },
    {
      "stream":  "rtsp://admin:PASSWORD@192.168.1.21:554/cam/realmonitor?channel=1&subtype=0",
      "name":  "East Camera"
    },
    {
      "stream":  "rtsp://admin:PASSWORD@192.168.1.22:554/cam/realmonitor?channel=1&subtype=0",
      "name":  "North Camera"
    }
  ],
  "grid_view": {
    "enable": false,
    "size": 2,
    "cameras": [
      {
        "stream":  "rtsp://admin:PASSWORD@192.168.1.23:554/cam/realmonitor?channel=1&subtype=1",
        "name":  "Patio Camera"
      },
      {
        "stream":  "rtsp://admin:PASSWORD@192.168.1.21:554/cam/realmonitor?channel=1&subtype=1",
        "name":  "East Camera"
      },
      {
        "stream":  "rtsp://admin:PASSWORD@192.168.1.22:554/cam/realmonitor?channel=1&subtype=1",
        "name":  "North Camera"
      }
    ]
  },
  "resolution": [640, 480],
  "mini_resolution": [320, 240],
  "arrow_gpios": [13, 21, 5],
  "enable_gpio": true,
  "keys": [16777234, 16777236, 32],
  "clock": true,
  "name": true,
  "arrows": true,
  "no_cursor": true
}
```

### resolution
* Must be the same aspect ratio as the original source
* Ex: `[640, 480]`

### mini_resolution
* Resolution used in the grid view
* Must be the same aspect ratio as the original source
* Ex: `[320, 240]`

### Common values for "keys"
* Up: 16777235
* Down: 16777237
* Left: 16777234
* Right: 16777236
* Shift: 16777248
* Space: 32