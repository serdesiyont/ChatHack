import { useState, useEffect } from "react";
import { vapi, startAssistant, stopAssistant } from "./ai";
import ActiveCallDetails from "./call/ActivaCallDetails";

function App() {
  const [started, setStarted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [assistantIsSpeaking, setAssistantIsSpeaking] = useState(false);
  const [volumeLevel, setVolumeLevel] = useState(0);
  const [callId, setCallId] = useState("");
  const [callResult, setCallResult] = useState(null);
  const [loadingResult, setLoadingResult] = useState(false);

  useEffect(() => {
    vapi
      .on("call-start", () => {
        setLoading(false);
        setStarted(true);
      })
      .on("call-end", () => {
        setStarted(false);
        setLoading(false);
      })
      .on("speech-start", () => {
        setAssistantIsSpeaking(true);
      })
      .on("speech-end", () => {
        setAssistantIsSpeaking(false);
      })
      .on("volume-level", (level) => {
        setVolumeLevel(level);
      });
  }, []);

  const handleStart = async () => {
    setLoading(true);
    const data = await startAssistant();
    if (data?.id) {
      setCallId(data.id);
    } else {
      console.error("Failed to start assistant or get call ID");
      setLoading(false);
    }
  };

  const handleStop = () => {
    stopAssistant();
    // Reset state to return to starting page
    setStarted(false);
    setCallId("");
    setCallResult(null);
    setLoadingResult(false);
    setLoading(false);
    // Optionally: If you want to still fetch call details, comment out the above and use the old logic
    // if (callId) {
    //   getCallDetails();
    // }
  };

  const getCallDetails = (interval = 3000) => {
    setLoadingResult(true);
    fetch("/call-details?call_id=" + callId)
      .then((response) => response.json())
      .then((data) => {
        if (data.analysis && data.summary) {
          console.log(data);
          setCallResult(data);
          setLoadingResult(false);
        } else {
          setTimeout(() => getCallDetails(interval), interval);
        }
      })
      .catch((error) => alert(error));
  };

  const showStartButton = !loading && !started && !loadingResult && !callResult;

  return (
    <div className="app-container">
      {showStartButton && (
        <>
          {!started && (
            <button onClick={handleStart} className="button">
              Start Conversation
            </button>
          )}
        </>
      )}
      {loadingResult && <p>Loading call details... please wait</p>}
      {!loadingResult && callResult && (
        <div className="call-result">
          <p>
            Qualified:{" "}
            {callResult.analysis.structuredData.is_qualified.toString()}
          </p>
          <p>{callResult.summary}</p>
        </div>
      )}
      {(loading || loadingResult) && <div className="loading"></div>}
      {started && (
        <ActiveCallDetails
          assistantIsSpeaking={assistantIsSpeaking}
          volumeLevel={volumeLevel}
          endCallCallback={handleStop}
        />
      )}
    </div>
  );
}

export default App;
