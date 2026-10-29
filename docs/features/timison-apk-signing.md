# Timison Browser Next APK signing

## Signing identity and local builds

Every Timison APK for package ID `com.timison.browser.next.full.agent.debug` must be signed by the dedicated Timison Browser Next key. The `timison` product flavor owns this signing configuration; Fulguris flavors continue using their existing signing configurations. Timison APK assembly fails when its signing environment is incomplete. The build tool also rejects the output unless its package ID and signing certificate fingerprint match the configured values.

Keep the keystore outside the repository in an access-controlled backup location. Provide the local build process these environment values without putting them in shell history or checked-in Gradle properties:

```sh
export TIMISON_SIGNING_STORE_FILE="$HOME/.config/timison-signing/timison-browser-next.jks"
export TIMISON_SIGNING_KEY_ALIAS="timison-browser-next"
export TIMISON_SIGNING_CERT_SHA256="<64 hex digits from the certificate SHA-256 fingerprint>"
read -s "TIMISON_SIGNING_STORE_PASSWORD?Keystore password: "; echo
export TIMISON_SIGNING_STORE_PASSWORD
read -s "TIMISON_SIGNING_KEY_PASSWORD?Key password: "; echo
export TIMISON_SIGNING_KEY_PASSWORD
python scripts/tools/build.py --build-type timisonDebug
```

`scripts/tools/build.py` uses Gradle's `timison` flavor signing config, then verifies the APK with Android SDK `aapt` and `apksigner`. Missing credentials, an unsigned APK, a package mismatch, multiple signers, or any certificate fingerprint mismatch is a hard failure. Fulguris builds do not need the Timison key.

## GitHub Actions configuration

The `Timison Browser Next` workflow requires these repository Actions secrets:

- `TIMISON_KEYSTORE_BASE64`: base64 encoding of the JKS keystore bytes.
- `TIMISON_SIGNING_STORE_PASSWORD`
- `TIMISON_SIGNING_KEY_ALIAS`
- `TIMISON_SIGNING_KEY_PASSWORD`

It also requires the repository Actions variable `TIMISON_SIGNING_CERT_SHA256`, containing the lowercase or uppercase hex SHA-256 certificate fingerprint (colons are accepted). The public fingerprint is a pin, not a secret. The workflow decodes the keystore under `$RUNNER_TEMP` with mode 0600, builds, validates the exact package and certificate, checks the Timison launcher label, and only then uploads the APK artifact. It never downloads or writes a signing key into the repository. A run without these secrets/variable fails before artifact publication; configure them in GitHub → repository Settings → Secrets and variables → Actions. Keep the existing draft PR open until a signed workflow run succeeds.

Do not paste passwords into source files, issue/PR text, command arguments, or agent chat. Use GitHub's secret UI or a secure local terminal workflow to provision values.

## Key creation, backup, rotation, and recovery

The signing key is a long-lived update identity. Loss of the private key can make future in-place updates impossible; compromise requires treating the key as exposed and planning a new package identity or an explicit reinstall.

1. On a trusted Mac, create a protected directory outside the repository with `mkdir -p "$HOME/.config/timison-signing" && chmod 700 "$HOME/.config/timison-signing"`. Use `keytool -genkeypair -keystore "$HOME/.config/timison-signing/timison-browser-next.jks" -alias timison-browser-next -keyalg RSA -keysize 4096 -validity 10000`. Enter the password interactively; do not put it on the command line. Record the certificate SHA-256 fingerprint from `keytool -list -v -keystore ...` and compare it with `apksigner verify --print-certs` on a locally built APK.
2. Keep at least two encrypted, access-controlled backups of the keystore in separate trusted locations. Record the alias, password recovery method, and fingerprint in a password manager. Periodically restore a backup to a separate directory and verify that it can sign a test APK.
3. Add the credentials only to the four named GitHub Actions secrets and pin the public fingerprint as the Actions variable. Local builds use the same backed-up keystore and the same pin.
4. Rotate only through a planned release. Android generally rejects an update signed by a different certificate. A new key therefore cannot update an installation signed by the old key unless a supported signing lineage is configured and verified for the relevant Android versions. This project does not configure signing lineage.
5. If the old private key is lost or compromised, stop publishing updates under an unverified key. A fallback migration requires a user-approved export/backup of browser data where supported, explicit removal of the old package, then installation of a build signed by the replacement key. Normal uninstall removes private app data, including cookies, sessions, and local settings; bookmarks/history may require an app-provided export and must be checked before uninstall. This recovery is not automatic and may lose data.

## Existing installation migration

The reported run 40803084277 artifact was rejected by Android because its signing certificate differs from the currently installed package certificate. The new dedicated key will also differ from that old certificate unless the private key used for the existing install is recovered and proven. This work does not claim an in-place update or data preservation across the signer change.

Before migrating, export bookmarks using the browser's own export UI if available, and separately record any other data that matters. A one-time uninstall/reinstall can be required to move to the stable identity, and Android uninstall can erase app-private data. The Mac auto-deployment script never uninstalls the application. It verifies package and signer before prompting, then invokes only `adb install -r`; any installation signature error is reported without retrying via uninstall.

The certificate can only be called established after a real key is provisioned in the trusted local store, matching GitHub secrets/variable are configured, and a hosted build passes certificate verification. No key material belongs in Git.

Platform reference: [Android app signing](https://developer.android.com/studio/publish/app-signing) explains signing identity continuity for updates and supported signing key rotation lineages. This project does not have a configured lineage.
