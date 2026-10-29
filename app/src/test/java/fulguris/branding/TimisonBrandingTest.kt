package fulguris.branding

import org.assertj.core.api.Assertions.assertThat
import org.junit.Test

class TimisonBrandingTest {
    private val timisonPackage = "com.timison.browser.next.full.agent.debug"
    private val fulgurisPackage = "net.slions.fulguris.full.agent.debug"

    @Test
    fun `branding is restricted to the Timison package`() {
        assertThat(TimisonBranding.isTimison(timisonPackage)).isTrue()
        assertThat(TimisonBranding.isTimison(fulgurisPackage)).isFalse()
        assertThat(TimisonBranding.homeHeader(fulgurisPackage)).isEmpty()
        assertThat(TimisonBranding.bookmarksHeader(fulgurisPackage)).isEmpty()
    }

    @Test
    fun `Timison pages show Home status and keep TARP unavailable`() {
        listOf(
            TimisonBranding.homeHeader(timisonPackage),
            TimisonBranding.bookmarksHeader(timisonPackage)
        ).forEach { header ->
            assertThat(header).contains("Timison Browser Next")
                .contains("HOME · ACTIVE")
                .contains("Android system networking")
                .contains("TARP · UNAVAILABLE")
                .contains("aria-disabled=\"true\"")
                .contains("leak prevention are verified")
        }
    }
}
