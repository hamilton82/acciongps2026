import 'dart:ui' show Color;

class ServerOption {
  const ServerOption({
    required this.title,
    required this.url,
    required this.color,
    this.assetPath,
    this.subtitle,
  });

  final String title;
  final String url;
  final Color color;
  final String? assetPath;
  final String? subtitle;
}

class AppConfig {
  static const appName = 'Accion GPS';
  static const packageId = 'org.acciongps.manager';
  static const scheme = 'org.acciongps.manager';

  static const defaultAssetPath = 'assets/icono.png';

  static const servers = <ServerOption>[
    ServerOption(
      title: 'AccionGps',
      subtitle: "Server Principal",
        url: 'https://server.acciongps.com/login',
      assetPath: defaultAssetPath,
      color: Color(0xFF1565C0),
    ),
    ServerOption(
      title: 'Devs AccionGPS',
      subtitle: "Server Demo",
        url: 'https://devs.acciongps.com/login',
      assetPath: defaultAssetPath,
      color: Color(0xFF2196F3),
    ),
  ];

  static String get defaultUrl => servers.first.url;
}
