package fulguris.extensions

import fulguris.SDK_VERSION
import fulguris.TestApplication
import org.assertj.core.api.Assertions.assertThat
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.Closeable

/** Unit tests for [Closeable] extensions. */
@RunWith(RobolectricTestRunner::class)
@Config(application = TestApplication::class, sdk = [SDK_VERSION])
class CloseableExtensionsTest {

    @Test
    fun `safeUse returns block result and closes resource`() {
        var closed = false
        val closeable = Closeable { closed = true }

        val result = closeable.safeUse { "parsed" }

        assertThat(result).isEqualTo("parsed")
        assertThat(closed).isTrue()
    }

    @Test
    fun `safeUse absorbs block exception and closes resource`() {
        var closed = false
        val closeable = Closeable { closed = true }

        val result = closeable.safeUse { _: Closeable -> throw IllegalStateException("parse failed") }

        assertThat(result == null).isTrue()
        assertThat(closed).isTrue()
    }
}
