import 'package:flutter/material.dart';
import '../services/audio_service.dart';
import 'dart:async';

class VoiceInputButton extends StatefulWidget {
  final Function(String) onTranscribed;

  const VoiceInputButton({
    Key? key,
    required this.onTranscribed,
  }) : super(key: key);

  @override
  State<VoiceInputButton> createState() => _VoiceInputButtonState();
}

class _VoiceInputButtonState extends State<VoiceInputButton>
    with SingleTickerProviderStateMixin {
  final AudioService _audioService = AudioService();
  bool _isRecording = false;
  bool _isTranscribing = false;
  late AnimationController _animationController;
  Stopwatch _recordingStopwatch = Stopwatch();
  Timer? _recordingTimer;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    _recordingTimer?.cancel();
    super.dispose();
  }

  String _formatDuration(Duration duration) {
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    String minutes = twoDigits(duration.inMinutes.remainder(60));
    String seconds = twoDigits(duration.inSeconds.remainder(60));
    return '$minutes:$seconds';
  }

  Future<void> _startRecording() async {
    final hasPermission = await _audioService.startRecording();
    if (hasPermission) {
      setState(() => _isRecording = true);
      _animationController.repeat();
      _recordingStopwatch.start();
      _recordingTimer = Timer.periodic(const Duration(seconds: 1), (_) {
        setState(() {});
      });
    } else {
      Future.delayed(const Duration(seconds: 2), () {
        if (mounted) _showStatus('Microphone permission denied');
      });
    }
  }

  Future<void> _stopRecording() async {
    final audioPath = await _audioService.stopRecording();
    setState(() {
      _isRecording = false;
      _isTranscribing = true;
    });
    _animationController.stop();
    _animationController.reset();
    _recordingStopwatch.stop();
    _recordingStopwatch.reset();
    _recordingTimer?.cancel();

    if (audioPath != null) {
      final transcribedText = await _audioService.transcribeAudio(audioPath);
      
      setState(() => _isTranscribing = false);
      
      if (transcribedText != null) {
        widget.onTranscribed(transcribedText);
      }
    }
  }

  void _showStatus(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 48,
      height: 48,
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          if (_isRecording)
            Positioned(
              bottom: 64,
              left: 0,
              right: 0,
              child: Center(
                child: Text(
                  _formatDuration(_recordingStopwatch.elapsed),
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          Center(
            child: GestureDetector(
              onTap: _isTranscribing ? null : (_isRecording ? _stopRecording : _startRecording),
              child: AnimatedBuilder(
                animation: _animationController,
                builder: (context, child) {
                  return Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: _isRecording
                          ? Color.lerp(
                              Theme.of(context).colorScheme.error,
                              Theme.of(context).colorScheme.errorContainer,
                              _animationController.value,
                            )
                          : Colors.transparent,
                    ),
                    child: _isTranscribing
                        ? SizedBox(
                            width: 24,
                            height: 24,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                Theme.of(context).colorScheme.primary,
                              ),
                            ),
                          )
                        : Icon(
                            _isRecording ? Icons.stop : Icons.mic,
                            color: _isRecording
                                ? Theme.of(context).colorScheme.onError
                                : Theme.of(context).colorScheme.onSurfaceVariant,
                            size: 24,
                          ),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}
