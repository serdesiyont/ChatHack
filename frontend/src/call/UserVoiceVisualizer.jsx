import VolumeLevel from "./VolumeLevel";

const UserVoiceVisualizer = ({ volume }) => {
  return (
    <div className="user-volume-visualizer">
      <VolumeLevel volume={volume} />
    </div>
  );
};

export default UserVoiceVisualizer;
