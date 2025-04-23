const AssistantVoiceVisualizer = ({ isSpeaking, volumeLevel }) => {
  return (
    <div className="assistant-visualizer">
      <p className="visualizer-label">Assistant:</p>
      <div
        className="indicators-container"
        style={{ display: "flex", gap: "8px", alignItems: "center" }}
      >
        {/* Assistant Indicator */}
        <div
          className={`speech-indicator ${
            isSpeaking ? "speaking" : "not-speaking"
          }`}
          title="Assistant Speaking Status"
        ></div>
        {/* User Indicator */}
        {/* (User indicator code can be added here if needed) */}
      </div>
    </div>
  );
};

export default AssistantVoiceVisualizer;
