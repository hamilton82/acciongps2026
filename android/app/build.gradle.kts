import java.util.Properties
import java.io.FileInputStream

plugins {
    id("com.android.application")
    // START: FlutterFire Configuration
    id("com.google.gms.google-services")
    id("com.google.firebase.crashlytics")
    // END: FlutterFire Configuration
    id("kotlin-android")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

val keystoreProperties = Properties()
val keystorePropertiesFile = file("key.properties")
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(FileInputStream(keystorePropertiesFile))
}

android {
    namespace = "org.acciongps.manager"
    compileSdk = 37
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_17.toString()
    }

    defaultConfig {
        applicationId = "org.acciongps.manager"
        // You can update the following values to match your application needs.
        // For more information, see: https://flutter.dev/to/review-gradle-config.
        minSdk = flutter.minSdkVersion
        targetSdk = 37
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    signingConfigs {
        create("release") {
            enableV1Signing = true
            keyAlias = keystoreProperties["keyAlias"] as? String ?: "androiddebugkey"
            keyPassword = keystoreProperties["keyPassword"] as? String ?: "android"
            storeFile = if (keystorePropertiesFile.exists()) {
                keystoreProperties["storeFile"]?.let { file(it) }
            } else {
                file(System.getProperty("user.home") + "/.android/debug.keystore")
            }
            storePassword = keystoreProperties["storePassword"] as? String ?: "android"
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
}

flutter {
    source = "../.."
}

afterEvaluate {
    tasks.named("assembleRelease").configure {
        doLast {
            val apkDir = file("${rootProject.projectDir}/../output")
            apkDir.mkdirs()
            val srcApk = file("${buildDir}/outputs/flutter-apk/app-release.apk")
            if (srcApk.exists()) {
                srcApk.copyTo(file("${apkDir}/AccionGPS.apk"), overwrite = true)
                println("APK copied to: ${apkDir}/AccionGPS.apk")
            }
        }
    }
}




