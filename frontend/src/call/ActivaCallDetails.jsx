import AssistantVoiceVisualizer from "./AssistantVoiceVisualizer";
import UserVoiceVisualizer from "./UserVoiceVisualizer";

const ActiveCallDetails = ({
  assistantIsSpeaking,
  volumeLevel,
  endCallCallback,
}) => {
  return (
    <div className="active-call-detail">
      <div className="call-info">
        <AssistantVoiceVisualizer
          isSpeaking={assistantIsSpeaking}
          volumeLevel={volumeLevel}
        />
        <UserVoiceVisualizer volume={volumeLevel} />
      </div>
      <div className="end-call-button">
        <button onClick={endCallCallback}>End Call</button>
      </div>
    </div>
  );
};

export default ActiveCallDetails;
