import 'package:flutter/material.dart';
import '../services/audio_service.dart';

class VoiceInputButton extends StatefulWidget {
  final Function(String) onTranscribed;

  const VoiceInputButton({
    Key? key,
    required this.onTranscribed,
  }) : super(key: key);

  @override
  State<VoiceInputButton> createState() => _VoiceInputButtonState();
}

class _VoiceInputButtonState extends State<VoiceInputButton> with SingleTickerProviderStateMixin {
  final AudioService _audioService = AudioService();
  bool _isRecording = false;
  late AnimationController _animationController;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  Future<void> _toggleRecording() async {
    if (!_isRecording) {
      final hasPermission = await _audioService.startRecording();
      if (hasPermission) {
        setState(() => _isRecording = true);
        _animationController.repeat(reverse: true);
        
        // Show recording indicator
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Recording... Tap the mic again to stop'),
            duration: Duration(days: 365), // Long duration, will be dismissed manually
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Microphone permission denied')),
        );
      }
    } else {
      final audioPath = await _audioService.stopRecording();
      setState(() => _isRecording = false);
      _animationController.stop();
      _animationController.reset();
      
      // Dismiss the recording indicator
      ScaffoldMessenger.of(context).hideCurrentSnackBar();
      
      if (audioPath != null) {
        // Show transcribing indicator
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Transcribing...')),
        );
        
        final transcribedText = await _audioService.transcribeAudio(audioPath);
        if (transcribedText != null) {
          widget.onTranscribed(transcribedText);
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Failed to transcribe audio')),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animationController,
      builder: (context, child) {
        return IconButton(
          icon: Icon(_isRecording ? Icons.mic : Icons.mic_none),
          onPressed: _toggleRecording,
          color: _isRecording 
            ? Color.lerp(Colors.red, Colors.pink, _animationController.value)
            : null,
        );
      },
    );
  }
}
