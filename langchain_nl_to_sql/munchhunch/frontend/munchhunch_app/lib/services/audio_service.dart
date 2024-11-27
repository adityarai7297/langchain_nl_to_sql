import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:dio/dio.dart';

class ApiService {
  final Dio _dio;

  ApiService() : 
    _dio = Dio() {
    _dio.options.baseUrl = 'http://localhost:8006/api';
    _dio.options.headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
  }

  Future<String?> transcribeAudio(String audioPath) async {
    try {
      final formData = FormData.fromMap({
        'audio': await MultipartFile.fromFile(audioPath),
      });

      final response = await _dio.post(
        '/v1/speech-to-text/',
        data: formData,
        options: Options(
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        ),
      );

      if (response.statusCode == 200) {
        return response.data['text'];
      }
      return null;
    } catch (e) {
      print('Error transcribing audio: $e');
      return null;
    }
  }

  // ... existing methods (processFoodEntry, getFoodEntries) ...
}

class AudioService {
  final ApiService _apiService;
  final _audioRecorder = Record();
  String? _currentRecordingPath;

  AudioService() : _apiService = ApiService();

  Future<bool> startRecording() async {
    try {
      if (await _audioRecorder.hasPermission()) {
        final directory = await getTemporaryDirectory();
        final filePath = '${directory.path}/audio_message.wav';
        _currentRecordingPath = filePath;
        
        final fileUrl = Uri.file(filePath).toString();
        
        await _audioRecorder.start(
          path: fileUrl,
          encoder: AudioEncoder.wav,
          bitRate: 16000,
          samplingRate: 16000,
          numChannels: 1,
        );
        return true;
      }
      return false;
    } catch (e) {
      print('Error starting recording: $e');
      return false;
    }
  }

  Future<String?> stopRecording() async {
    try {
      await _audioRecorder.stop();
      // If _currentRecordingPath is a URL, convert it back to a path
      if (_currentRecordingPath?.startsWith('file://') ?? false) {
        return Uri.parse(_currentRecordingPath!).toFilePath();
      }
      return _currentRecordingPath;
    } catch (e) {
      print('Error stopping recording: $e');
      return null;
    }
  }

  Future<String?> transcribeAudio(String audioPath) async {
    try {
      final transcribedText = await _apiService.transcribeAudio(audioPath);
      return transcribedText;
    } catch (e) {
      print('Error transcribing audio: $e');
      return null;
    } finally {
      // Clean up the temporary file
      try {
        await File(audioPath).delete();
      } catch (e) {
        print('Error deleting temporary file: $e');
      }
    }
  }
} 