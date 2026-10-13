#!/usr/bin/env python3
"""
REBRANDING 2026
===============
Saves config in rebrand_config.json for reuse.
"""
import json, os, re, shutil, sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

MIPOPSIZES = {
    "mdpi": (48, 108),
    "hdpi": (72, 162),
    "xhdpi": (96, 216),
    "xxhdpi": (144, 324),
    "xxxhdpi": (192, 432),
}

COLORS = [
    "Color(0xFF1565C0)", "Color(0xFF2196F3)",
    "Color(0xFF2E7D32)", "Color(0xFF4CAF50)",
]

class Rebrander2026:
    def __init__(self):
        self.root = Path(__file__).resolve().parent
        self.package = None
        self.app_name = None
        self.scheme = None
        self.icon_source = "assets/icono.png"
        self.servers = []
        self.bg_color = "#0A4FA0"
        self.version_code = 100
        self.version_name = "2026.2.0"
        self.target_sdk = 37

    def _config_path(self):
        return self.root / "rebrand_config.json"

    def _save_config(self):
        config = {
            "package": self.package, "app_name": self.app_name,
            "scheme": self.scheme, "icon_source": self.icon_source,
            "bg_color": self.bg_color, "version_code": self.version_code,
            "version_name": self.version_name, "target_sdk": self.target_sdk,
            "servers": self.servers,
        }
        self._config_path().write_text(
            json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"\n  Config saved: {self._config_path().name}")

    def _load_config(self):
        p = self._config_path()
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _read_package_from_firebase(self):
        gs = self.root / "assets" / "google-services.json"
        if gs.exists():
            try:
                data = json.loads(gs.read_text(encoding="utf-8"))
                for client in data.get("client", []):
                    ci = client.get("client_info", {})
                    if "android_client_info" in ci:
                        return ci["android_client_info"].get("package_name", "")
            except Exception:
                pass
        plist = self.root / "assets" / "GoogleService-Info.plist"
        if plist.exists():
            try:
                c = plist.read_text(encoding="utf-8")
                m = re.search(r"<key>BUNDLE_ID</key>\s*<string>([^<]+)</string>", c)
                if m:
                    return m.group(1)
            except Exception:
                pass
        return None

    def _find_android_client(self, data):
        """Find android client info. Returns dict with keys:
        api_key, app_id, package, project_id, project_number, storage_bucket"""
        result = {}
        for client in data.get("client", []):
            ci = client.get("client_info", {})
            if "android_client_info" in ci:
                ai = ci["android_client_info"]
                result["package"] = ai.get("package_name", "")
                result["app_id"] = ci.get("mobilesdk_app_id", "")
                break
        # api_key from first client's api_key array
        for client in data.get("client", []):
            for ak in client.get("api_key", []):
                if ak.get("current_key"):
                    result["api_key"] = ak["current_key"]
                    break
            if "api_key" in result:
                break
        proj = data.get("project_info", {})
        result["project_id"] = proj.get("project_id", "")
        result["project_number"] = proj.get("project_number", "")
        result["storage_bucket"] = proj.get("storage_bucket", "")
        return result

    def _find_ios_from_plist(self, plist_text):
        """Read iOS Firebase values from GoogleService-Info.plist"""
        def val(key):
            m = re.search(rf"<key>{key}</key>\s*<string>([^<]+)</string>", plist_text)
            return m.group(1) if m else ""
        return {
            "api_key": val("API_KEY"),
            "app_id": val("GOOGLE_APP_ID"),
            "project_id": val("PROJECT_ID"),
            "project_number": val("GCM_SENDER_ID"),
            "storage_bucket": val("STORAGE_BUCKET"),
            "bundle_id": val("BUNDLE_ID"),
        }

    def _ask_clone(self):
        print("=" * 55)
        print("  REBRANDING 2026")
        print("=" * 55)
        print("\n  [C]lonar a carpeta nueva  o  [R]ebrandear esta carpeta?")
        mode = input("  (C/R): ").strip().lower()
        if mode != "c":
            return
        name = input("\n  Nombre de la carpeta nueva: ").strip()
        if not name:
            print("  Cancelado.")
            sys.exit(0)
        dest = self.root.parent / name
        if dest.exists():
            print(f"  Ya existe: {dest}")
            sys.exit(0)
        print(f"\n  Copiando solo codigo fuente a {dest} ...")
        exclude = {
            "build", ".dart_tool", "output", ".gradle", ".kotlin",
            ".idea", ".vscode", "android/app/build", "android/.gradle",
            "ios/Pods", "ios/.symlinks", "linux/build", "macos/build",
            "windows/build", "web/icons",
        }
        def ignore(src, names):
            ignored = set()
            for n in names:
                rel = str(Path(src, n).relative_to(self.root))
                if n in ("java_pid",) or n.endswith(".hprof"):
                    ignored.add(n)
                    continue
                for ex in exclude:
                    if rel.startswith(ex) or rel == ex:
                        ignored.add(n)
                        break
            return ignored
        shutil.copytree(self.root, dest, ignore=ignore)
        for leftover in dest.rglob("java_pid*.hprof"):
            leftover.unlink()
        for leftover in dest.rglob("*.hprof"):
            leftover.unlink()
        out = dest / "output"
        if out.is_file():
            out.unlink()
        out.mkdir(exist_ok=True)
        print(f"  Listo: {dest}")
        print(f"  Ejecuta el script desde ahi: python {dest / 'rebrand_2026.py'}")
        sys.exit(0)

    def get_user_input(self):
        self._ask_clone()

        saved = self._load_config()

        if saved:
            print("\n  Previous config found:")
            print(f"    Package : {saved.get('package', '')}")
            print(f"    App     : {saved.get('app_name', '')}")
            print(f"    Servers : {len(saved.get('servers', []))}")
            for i, s in enumerate(saved.get('servers', []), 1):
                print(f"      {i}. {s.get('title', '')} -> {s.get('url', '')}")
            print(f"    Version : {saved.get('version_name', '')} (code: {saved.get('version_code', '')})")

            mode = input("\n  [N]ueva config  o  [E]ditar guardada? (N/E): ").strip().lower()
            if mode == "e":
                return self._edit_saved(saved)
            print()

        detected = self._read_package_from_firebase()
        if detected:
            print(f"\n  Package detected: {detected}")
            self.package = input(f"  Package (Enter='{detected}'): ").strip() or detected
        else:
            self.package = input("\n  Package (default: org.acciongps.manager): ").strip() or "org.acciongps.manager"

        self.app_name = input("  App name: ").strip() or "AccionGPS Manager"
        self.scheme = self.package
        self._input_servers()
        self._input_extras()
        self._show_confirm()
        return input("\n  Continue? (s/N): ").strip().lower() in ("s", "si", "sí", "y", "yes")

    def _edit_saved(self, saved):
        self.package = saved.get("package", "")
        self.app_name = saved.get("app_name", "")
        self.scheme = saved.get("scheme", self.package)
        self.icon_source = saved.get("icon_source", "assets/icono.png")
        self.bg_color = saved.get("bg_color", "#0A4FA0")
        self.version_code = saved.get("version_code", 100)
        self.version_name = saved.get("version_name", "2026.2.0")
        self.target_sdk = saved.get("target_sdk", 37)
        self.servers = list(saved.get("servers", []))

        print("\n  What to change?")
        print("    1. Servers")
        print("    2. Version")
        print("    3. Icon")
        print("    4. All")
        print("    5. Nothing (re-build)")
        choice = input("  Option (1-5): ").strip()

        if choice == "1":
            self._input_servers()
        elif choice == "2":
            self._input_version()
        elif choice == "3":
            self._input_icon()
        elif choice == "4":
            self._input_servers()
            self._input_version()
            self._input_icon()

        self._show_confirm()
        return input("\n  Continue? (s/N): ").strip().lower() in ("s", "si", "sí", "y", "yes")

    def _input_servers(self):
        print("\n  --- Servers ---")
        num = input("  How many servers? (Enter=keep current): ").strip()
        if num == "" and self.servers:
            print(f"  Keeping {len(self.servers)} servers")
            return
        num = int(num) if num.isdigit() and int(num) > 0 else len(self.servers) or 4
        defaults = [
            "https://server.acciongps.com",
            "https://server.acciongps.com",
            "https://devs.acciongps.com",
            "https://devs.acciongps.com",
        ]
        self.servers = []
        for i in range(1, num + 1):
            print(f"\n  --- Server #{i} ---")
            t = input(f"  Title: ").strip() or f"Server {i}"
            u = input(f"  URL: ").strip() or (defaults[i - 1] if i <= len(defaults) else defaults[0])
            sub = input(f"  Subtitle (optional): ").strip()
            self.servers.append({"title": t, "url": u, "subtitle": sub})

    def _input_version(self):
        print("\n  --- Version ---")
        vc = input(f"  versionCode (current: {self.version_code}): ").strip()
        if vc.isdigit():
            self.version_code = int(vc)
        vn = input(f"  versionName (current: {self.version_name}): ").strip()
        if vn:
            self.version_name = vn
        sdk = input(f"  targetSdk (current: {self.target_sdk}): ").strip()
        if sdk.isdigit() and int(sdk) >= 35:
            self.target_sdk = int(sdk)

    def _input_icon(self):
        print("\n  --- Icon ---")
        self.icon_source = input(f"  Icon source (current: {self.icon_source}): ").strip() or self.icon_source
        self.bg_color = input(f"  Background color (current: {self.bg_color}): ").strip() or self.bg_color

    def _input_extras(self):
        self._input_icon()
        self._input_version()

    def _show_confirm(self):
        print("\n  --- Confirm ---")
        print(f"  Package : {self.package}")
        print(f"  App     : {self.app_name}")
        print(f"  Scheme  : {self.scheme}")
        print(f"  Servers :")
        for i, s in enumerate(self.servers, 1):
            print(f"    {i}. {s['title']} -> {s['url']}")
        print(f"  Icon    : {self.icon_source}")
        print(f"  Color   : {self.bg_color}")
        print(f"  Version : {self.version_name} (code: {self.version_code})")
        print(f"  SDK     : {self.target_sdk}")

    # ------------------------------------------------------------------
    # Icon generation
    # ------------------------------------------------------------------
    def generate_icons(self):
        src = self.root / self.icon_source
        if not src.exists():
            print(f"  Icon not found: {src}")
            return
        res_dir = self.root / "android" / "app" / "src" / "main" / "res"
        img = Image.open(src).convert("RGBA")
        for density, (ls, fs) in MIPOPSIZES.items():
            md = res_dir / f"mipmap-{density}"
            md.mkdir(parents=True, exist_ok=True)
            l = img.copy()
            l.thumbnail((ls, ls), Image.LANCZOS)
            l.save(md / "ic_launcher.png")
            f = img.copy()
            f.thumbnail((fs, fs), Image.LANCZOS)
            f.save(md / "ic_launcher_foreground.png")
        ad = res_dir / "mipmap-anydpi-v26"
        ad.mkdir(parents=True, exist_ok=True)
        (ad / "ic_launcher.xml").write_text(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
            '    <background android:drawable="@color/ic_launcher_background"/>\n'
            '    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>\n'
            '</adaptive-icon>\n',
            encoding="utf-8",
        )
        cx = res_dir / "values" / "colors.xml"
        cx.parent.mkdir(parents=True, exist_ok=True)
        cx.write_text(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            f'<resources>\n    <color name="ic_launcher_background">{self.bg_color}</color>\n</resources>\n',
            encoding="utf-8",
        )
        print("  Icons generated")

    # ------------------------------------------------------------------
    # app_config.dart
    # ------------------------------------------------------------------
    def update_app_config(self):
        entries = []
        for i, s in enumerate(self.servers):
            sub = f'subtitle: "{s["subtitle"]}",\n        ' if s.get("subtitle") else ""
            entries.append(
                f"    ServerOption(\n"
                f"      title: '{s['title']}',\n"
                f"      {sub}url: '{s['url']}',\n"
                f"      assetPath: defaultAssetPath,\n"
                f"      color: {COLORS[i % len(COLORS)]},\n"
                f"    ),"
            )
        content = (
            "import 'dart:ui' show Color;\n"
            "\n"
            "class ServerOption {\n"
            "  const ServerOption({\n"
            "    required this.title,\n"
            "    required this.url,\n"
            "    required this.color,\n"
            "    this.assetPath,\n"
            "    this.subtitle,\n"
            "  });\n"
            "\n"
            "  final String title;\n"
            "  final String url;\n"
            "  final Color color;\n"
            "  final String? assetPath;\n"
            "  final String? subtitle;\n"
            "}\n"
            "\n"
            "class AppConfig {\n"
            f"  static const appName = '{self.app_name}';\n"
            f"  static const packageId = '{self.package}';\n"
            f"  static const scheme = '{self.scheme}';\n"
            "\n"
            "  static const defaultAssetPath = 'assets/icono.png';\n"
            "\n"
            "  static const servers = <ServerOption>[\n"
            + "\n".join(entries)
            + "\n  ];\n"
            "\n"
            "  static String get defaultUrl => servers.first.url;\n"
            "}\n"
        )
        (self.root / "lib" / "app_config.dart").write_text(content, encoding="utf-8")
        print("  lib/app_config.dart")

    # ------------------------------------------------------------------
    # AndroidManifest.xml
    # ------------------------------------------------------------------
    def update_android_manifest(self):
        p = self.root / "android" / "app" / "src" / "main" / "AndroidManifest.xml"
        if not p.exists():
            return
        c = p.read_text(encoding="utf-8")
        c = re.sub(r'android:label="[^"]*"', f'android:label="{self.app_name}"', c)
        c = re.sub(r'android:scheme="[^"]*"', f'android:scheme="{self.scheme}"', c)
        p.write_text(c, encoding="utf-8")
        print("  AndroidManifest.xml")

    # ------------------------------------------------------------------
    # build.gradle.kts
    # ------------------------------------------------------------------
    def update_build_gradle(self):
        p = self.root / "android" / "app" / "build.gradle.kts"
        if not p.exists():
            return
        c = p.read_text(encoding="utf-8")
        c = re.sub(r'namespace\s*=\s*"[^"]*"', f'namespace = "{self.package}"', c)
        c = re.sub(r'applicationId\s*=\s*"[^"]*"', f'applicationId = "{self.package}"', c)
        c = re.sub(r'compileSdk\s*=\s*\d+', f'compileSdk = {self.target_sdk}', c)
        c = re.sub(r'targetSdk\s*=\s*\d+', f'targetSdk = {self.target_sdk}', c)
        c = re.sub(r'rootProject\.file\("[^"]*key\.properties"\)', 'file("key.properties")', c)
        c = re.sub(r'isMinifyEnabled\s*=\s*false', 'isMinifyEnabled = true', c)
        c = re.sub(r'isShrinkResources\s*=\s*false', 'isShrinkResources = true', c)
        apk_name = self.app_name.replace(" ", "")
        c = re.sub(r'AccionGPS', apk_name, c)
        p.write_text(c, encoding="utf-8")
        print("  build.gradle.kts")

    # ------------------------------------------------------------------
    # MainActivity.kt
    # ------------------------------------------------------------------
    def update_main_activity(self):
        kt_base = self.root / "android" / "app" / "src" / "main" / "kotlin"
        old_dirs = [d.parent for d in kt_base.rglob("MainActivity.kt")]
        new_parts = self.package.split(".")
        target = kt_base
        for p in new_parts:
            target = target / p
        target.mkdir(parents=True, exist_ok=True)
        dest = target / "MainActivity.kt"
        for old_dir in old_dirs:
            src = old_dir / "MainActivity.kt"
            if src.exists() and src != dest:
                shutil.move(str(src), str(dest))
        if dest.exists():
            dest.write_text(
                f"package {self.package}\n\n"
                "import io.flutter.embedding.android.FlutterFragmentActivity\n\n"
                "class MainActivity : FlutterFragmentActivity()\n",
                encoding="utf-8",
            )
        print("  MainActivity.kt")

    # ------------------------------------------------------------------
    # Signing key
    # ------------------------------------------------------------------
    def update_signing_key(self):
        android_dir = self.root / "android" / "app"
        src_jks = self.root / "assets" / "upload-keystore.jks"
        src_props = self.root / "assets" / "key.properties"
        if not src_jks.exists() and not src_props.exists():
            print("  signing: no files in assets/")
            return
        if src_jks.exists():
            shutil.copy2(str(src_jks), str(android_dir / "upload-keystore.jks"))
            print("  upload-keystore.jks copied")
        if src_props.exists():
            content = src_props.read_text(encoding="utf-8")
            content = re.sub(r"storeFile\s*=\s*[^\n]*", "storeFile=upload-keystore.jks", content)
            content = re.sub(r"keyAlias\s*=\s*[^\n]*", "keyAlias=key0", content)
            (android_dir / "key.properties").write_text(content, encoding="utf-8")
            print("  key.properties copied")

    # ------------------------------------------------------------------
    # google-services.json
    # ------------------------------------------------------------------
    def update_proguard(self):
        p = self.root / "android" / "app" / "proguard-rules.pro"
        if not p.exists():
            return
        c = p.read_text(encoding="utf-8")
        c = re.sub(r"-keep class org\.\w+\.\*\*", f"-keep class {self.package.rsplit('.', 1)[0]}.**", c)
        p.write_text(c, encoding="utf-8")
        print("  proguard-rules.pro")

    def update_google_services(self):
        src = self.root / "assets" / "google-services.json"
        dst = self.root / "android" / "app" / "google-services.json"
        if src.exists():
            shutil.copy2(str(src), str(dst))
            print("  google-services.json")

    # ------------------------------------------------------------------
    # firebase_options.dart
    # ------------------------------------------------------------------
    def update_firebase_options(self):
        path = self.root / "lib" / "firebase_options.dart"
        if not path.exists():
            print("  firebase_options.dart not found")
            return

        # --- Android section from google-services.json ---
        gs_path = self.root / "assets" / "google-services.json"
        if not gs_path.exists():
            gs_path = self.root / "android" / "app" / "google-services.json"

        if gs_path.exists():
            try:
                data = json.loads(gs_path.read_text(encoding="utf-8"))
                android = self._find_android_client(data)
                c = path.read_text(encoding="utf-8")
                android_block = (
                    f"  static const FirebaseOptions android = FirebaseOptions(\n"
                    f"    apiKey: '{android['api_key']}',\n"
                    f"    appId: '{android['app_id']}',\n"
                    f"    messagingSenderId: '{android['project_number']}',\n"
                    f"    projectId: '{android['project_id']}',\n"
                    f"    storageBucket: '{android['storage_bucket']}',\n"
                    f"  );"
                )
                c = re.sub(
                    r"static const FirebaseOptions android = FirebaseOptions\([^)]+\);",
                    android_block,
                    c,
                    flags=re.DOTALL,
                )

                # --- iOS section from GoogleService-Info.plist ---
                plist_path = self.root / "assets" / "GoogleService-Info.plist"
                if plist_path.exists():
                    plist_text = plist_path.read_text(encoding="utf-8")
                    ios = self._find_ios_from_plist(plist_text)
                    ios_block = (
                        f"  static const FirebaseOptions ios = FirebaseOptions(\n"
                        f"    apiKey: '{ios['api_key']}',\n"
                        f"    appId: '{ios['app_id']}',\n"
                        f"    messagingSenderId: '{ios['project_number']}',\n"
                        f"    projectId: '{ios['project_id']}',\n"
                        f"    storageBucket: '{ios['storage_bucket']}',\n"
                        f"    iosBundleId: '{ios['bundle_id']}',\n"
                        f"  );"
                    )
                    c = re.sub(
                        r"static const FirebaseOptions ios = FirebaseOptions\([^)]+\);",
                        ios_block,
                        c,
                        flags=re.DOTALL,
                    )

                path.write_text(c, encoding="utf-8")
                print("  firebase_options.dart")
            except Exception as e:
                print(f"  firebase_options.dart error: {e}")
        else:
            print("  google-services.json not found")

    # ------------------------------------------------------------------
    # iOS
    # ------------------------------------------------------------------
    def update_ios(self):
        ios_dir = self.root / "ios"
        if not ios_dir.exists():
            return
        src_plist = self.root / "assets" / "GoogleService-Info.plist"
        dst_plist = ios_dir / "Runner" / "GoogleService-Info.plist"
        if src_plist.exists():
            shutil.copy2(str(src_plist), str(dst_plist))
            print("  ios/Runner/GoogleService-Info.plist")
        info = ios_dir / "Runner" / "Info.plist"
        if info.exists():
            c = info.read_text(encoding="utf-8")
            c = re.sub(
                r"<key>CFBundleDisplayName</key>\s*<string>[^<]*</string>",
                f"<key>CFBundleDisplayName</key>\n\t<string>{self.app_name}</string>",
                c,
            )
            info.write_text(c, encoding="utf-8")
            print("  ios/Runner/Info.plist")
        pbx = ios_dir / "Runner.xcodeproj" / "project.pbxproj"
        if pbx.exists():
            c = pbx.read_text(encoding="utf-8")
            for old in ["org.acciongps.manager", "org.traccar.manager", "com.example.traccarManager"]:
                c = c.replace(old, self.package)
            pbx.write_text(c, encoding="utf-8")
            print("  ios project.pbxproj")

    # ------------------------------------------------------------------
    # Version
    # ------------------------------------------------------------------
    def update_version(self):
        p = self.root / "android" / "app" / "build.gradle.kts"
        if p.exists():
            c = p.read_text(encoding="utf-8")
            c = re.sub(r"versionCode\s*=\s*\d+", f"versionCode = {self.version_code}", c)
            c = re.sub(r'versionName\s*=\s*"[^"]*"', f'versionName = "{self.version_name}"', c)
            c = re.sub(r"compileSdk\s*=\s*\d+", f"compileSdk = {self.target_sdk}", c)
            c = re.sub(r"targetSdk\s*=\s*\d+", f"targetSdk = {self.target_sdk}", c)
            p.write_text(c, encoding="utf-8")
            print("  build.gradle.kts (version + SDK)")
        pubspec = self.root / "pubspec.yaml"
        if pubspec.exists():
            c = pubspec.read_text(encoding="utf-8")
            c = re.sub(r"version:\s*\S+", f"version: {self.version_name}+{self.version_code}", c)
            pubspec.write_text(c, encoding="utf-8")
            print("  pubspec.yaml (version)")

    # ------------------------------------------------------------------
    # Main
    # ------------------------------------------------------------------
    def perform(self):
        print("\n--- Rebranding ---\n")
        self.generate_icons()
        self.update_app_config()
        self.update_version()
        self.update_android_manifest()
        self.update_build_gradle()
        self.update_main_activity()
        self.update_signing_key()
        self.update_proguard()
        self.update_google_services()
        self.update_firebase_options()
        self.update_ios()
        self._save_config()
        print("\n--- Next steps ---")
        print("  1. flutter clean")
        print("  2. flutter pub get")
        print("  3. flutter build appbundle --release  (AAB for Play Store)")
        print("  4. flutter build apk --release         (APK for direct install)")

    def run(self):
        if not self.get_user_input():
            print("Cancelled.")
            return
        self.perform()
        print("\nDone.")


if __name__ == "__main__":
    Rebrander2026().run()
