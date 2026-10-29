/*
 * The contents of this file are subject to the Common Public Attribution License Version 1.0.
 * See LICENSE-CPAL-1.0 for the specific language governing permissions and limitations.
 *
 * Timison-specific branding helpers for the Fulguris-derived application.
 * The original Fulguris project and its license notices remain attributed in the app.
 */
package fulguris.branding

/** Brand elements that appear only in the Timison product flavor. */
object TimisonBranding {
    private const val PACKAGE_PREFIX = "com.timison.browser.next."

    fun isTimison(packageName: String): Boolean = packageName.startsWith(PACKAGE_PREFIX)

    fun homeHeader(packageName: String): String = if (isTimison(packageName)) header() else ""

    fun bookmarksHeader(packageName: String): String = if (isTimison(packageName)) header() else ""

    private fun header() = """
        <section class="timison-brand" role="region" aria-label="Timison Browser Next and network mode">
            <svg class="timison-mark" viewBox="0 0 108 108" role="img" aria-label="Timison">
                <path fill="#5FE0C5" d="M27 28h54v13H61v39H47V41H27z"/>
            </svg>
            <div class="timison-copy">
                <h1>Timison Browser Next</h1>
                <div class="timison-modes" role="group" aria-label="Network mode">
                    <span class="timison-mode timison-mode-active" role="radio" aria-checked="true">HOME · ACTIVE</span>
                    <span class="timison-mode timison-mode-disabled" role="radio" aria-checked="false" aria-disabled="true">TARP · UNAVAILABLE</span>
                </div>
                <p class="timison-status">Home uses Android system networking and follows the active VPN route.</p>
                <p class="timison-unavailable">TARP remains unavailable until authenticated routing and leak prevention are verified.</p>
            </div>
        </section>
    """.trimIndent()
}
