package com.auracoach

import android.media.MediaCodec
import android.media.MediaExtractor
import android.media.MediaFormat
import android.net.Uri
import com.facebook.react.bridge.Promise
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReactContextBaseJavaModule
import com.facebook.react.bridge.ReactMethod
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileOutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.UUID
import kotlin.concurrent.thread
import kotlin.math.roundToInt

class AudioExtractorModule(private val reactContext: ReactApplicationContext) :
  ReactContextBaseJavaModule(reactContext) {

  override fun getName(): String = "AudioExtractor"

  @ReactMethod
  fun extractMonoPcmWav(inputUri: String, promise: Promise) {
    thread(name = "AuraCoachAudioExtractor") {
      try {
        val inputPath = uriToPath(inputUri)
        val output = File(reactContext.cacheDir, "auracoach-${UUID.randomUUID()}.wav")
        extract(inputPath, output)
        promise.resolve(Uri.fromFile(output).toString())
      } catch (error: Exception) {
        promise.reject("AUDIO_EXTRACTION_FAILED", error.message, error)
      }
    }
  }

  private fun uriToPath(inputUri: String): String {
    return if (inputUri.startsWith("file://")) {
      Uri.parse(inputUri).path ?: throw IllegalArgumentException("Invalid file URI")
    } else {
      inputUri
    }
  }

  private fun extract(inputPath: String, output: File) {
    val extractor = MediaExtractor()
    var codec: MediaCodec? = null
    try {
      extractor.setDataSource(inputPath)
      val trackIndex = selectAudioTrack(extractor)
      if (trackIndex < 0) {
        throw IllegalArgumentException("Recording does not contain an audio track")
      }
      extractor.selectTrack(trackIndex)

      val inputFormat = extractor.getTrackFormat(trackIndex)
      val mime = inputFormat.getString(MediaFormat.KEY_MIME)
        ?: throw IllegalArgumentException("Audio track has no MIME type")
      val decoder = MediaCodec.createDecoderByType(mime)
      codec = decoder
      decoder.configure(inputFormat, null, null, 0)
      decoder.start()

      val monoSamples = ByteArrayOutputStream()
      val bufferInfo = MediaCodec.BufferInfo()
      var outputFormat = decoder.outputFormat
      var sampleRate = inputFormat.getInteger(MediaFormat.KEY_SAMPLE_RATE)
      var channelCount = inputFormat.getInteger(MediaFormat.KEY_CHANNEL_COUNT)
      var inputDone = false
      var outputDone = false

      while (!outputDone) {
        if (!inputDone) {
          val inputBufferIndex = decoder.dequeueInputBuffer(TIMEOUT_US)
          if (inputBufferIndex >= 0) {
            val inputBuffer = decoder.getInputBuffer(inputBufferIndex)
              ?: throw IllegalStateException("Decoder input buffer unavailable")
            val sampleSize = extractor.readSampleData(inputBuffer, 0)
            if (sampleSize < 0) {
              decoder.queueInputBuffer(
                inputBufferIndex,
                0,
                0,
                0,
                MediaCodec.BUFFER_FLAG_END_OF_STREAM,
              )
              inputDone = true
            } else {
              decoder.queueInputBuffer(
                inputBufferIndex,
                0,
                sampleSize,
                extractor.sampleTime,
                0,
              )
              extractor.advance()
            }
          }
        }

        when (val outputBufferIndex = decoder.dequeueOutputBuffer(bufferInfo, TIMEOUT_US)) {
          MediaCodec.INFO_OUTPUT_FORMAT_CHANGED -> {
            outputFormat = decoder.outputFormat
            sampleRate = outputFormat.getInteger(MediaFormat.KEY_SAMPLE_RATE)
            channelCount = outputFormat.getInteger(MediaFormat.KEY_CHANNEL_COUNT)
          }
          MediaCodec.INFO_TRY_AGAIN_LATER -> Unit
          else -> {
            if (outputBufferIndex >= 0) {
              val outputBuffer = decoder.getOutputBuffer(outputBufferIndex)
              if (outputBuffer != null && bufferInfo.size > 0) {
                appendMonoPcm16(outputBuffer, bufferInfo.offset, bufferInfo.size, channelCount, monoSamples)
              }
              outputDone = bufferInfo.flags and MediaCodec.BUFFER_FLAG_END_OF_STREAM != 0
              decoder.releaseOutputBuffer(outputBufferIndex, false)
            }
          }
        }
      }

      writeWav(output, monoSamples.toByteArray(), sampleRate)
    } finally {
      codec?.stop()
      codec?.release()
      extractor.release()
    }
  }

  private fun selectAudioTrack(extractor: MediaExtractor): Int {
    for (index in 0 until extractor.trackCount) {
      val format = extractor.getTrackFormat(index)
      val mime = format.getString(MediaFormat.KEY_MIME)
      if (mime?.startsWith("audio/") == true) return index
    }
    return -1
  }

  private fun appendMonoPcm16(
    source: ByteBuffer,
    offset: Int,
    size: Int,
    channelCount: Int,
    output: ByteArrayOutputStream,
  ) {
    val data = source.duplicate().order(ByteOrder.LITTLE_ENDIAN)
    data.position(offset)
    data.limit(offset + size)
    val channels = channelCount.coerceAtLeast(1)

    while (data.remaining() >= channels * BYTES_PER_SAMPLE) {
      var sum = 0
      for (channel in 0 until channels) {
        sum += data.short.toInt()
      }
      val mono = (sum.toDouble() / channels).roundToInt().coerceIn(Short.MIN_VALUE.toInt(), Short.MAX_VALUE.toInt())
      output.write(mono and 0xff)
      output.write((mono shr 8) and 0xff)
    }
  }

  private fun writeWav(output: File, pcm: ByteArray, sampleRate: Int) {
    FileOutputStream(output).use { stream ->
      val dataSize = pcm.size
      val riffSize = dataSize + 36
      stream.write("RIFF".toByteArray(Charsets.US_ASCII))
      stream.writeIntLe(riffSize)
      stream.write("WAVE".toByteArray(Charsets.US_ASCII))
      stream.write("fmt ".toByteArray(Charsets.US_ASCII))
      stream.writeIntLe(16)
      stream.writeShortLe(1)
      stream.writeShortLe(1)
      stream.writeIntLe(sampleRate)
      stream.writeIntLe(sampleRate * BYTES_PER_SAMPLE)
      stream.writeShortLe(BYTES_PER_SAMPLE)
      stream.writeShortLe(16)
      stream.write("data".toByteArray(Charsets.US_ASCII))
      stream.writeIntLe(dataSize)
      stream.write(pcm)
    }
  }

  private fun FileOutputStream.writeIntLe(value: Int) {
    write(value and 0xff)
    write((value shr 8) and 0xff)
    write((value shr 16) and 0xff)
    write((value shr 24) and 0xff)
  }

  private fun FileOutputStream.writeShortLe(value: Int) {
    write(value and 0xff)
    write((value shr 8) and 0xff)
  }

  companion object {
    private const val TIMEOUT_US = 10_000L
    private const val BYTES_PER_SAMPLE = 2
  }
}
