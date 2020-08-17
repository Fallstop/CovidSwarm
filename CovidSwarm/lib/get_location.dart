import 'package:geolocator/geolocator.dart';
import 'package:permission_handler/permission_handler.dart';

class Pos {
  double longitude;
  double latitude;

  bool error = false;

  Pos(this.longitude, this.latitude);

  static Pos err() {
    var pos = Pos(0, 0);
    pos.error = true;
    return pos;
  }

  @override
  String toString() {
    return !error
        ? "{ long:" +
            longitude.toString() +
            ", lati : " +
            latitude.toString() +
            " }"
        : "error";
  }
}

Future<Pos> getPosition() async {
  var geoLocator = Geolocator();
  var permissionStatus = await Permission.location.status;
  var locationServicesEnabled = await geoLocator.isLocationServiceEnabled();
  if (permissionStatus == PermissionStatus.granted && locationServicesEnabled) {
    var pos = await geoLocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high);
    return Pos(pos.longitude, pos.latitude);
  } else {
    if (locationServicesEnabled) {
      await Permission.location.request();
    }
    return Pos.err();
  }
}
