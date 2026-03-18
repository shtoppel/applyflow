import { useState } from "react";
import ApplicationsPage from "@/pages/ApplicationsPage";
import RecentActivityWidget from "@/components/applications/RecentActivityWidget";

function App() {
  const [refreshToken, setRefreshToken] = useState(0);

  const handleGlobalRefresh = () => {
    setRefreshToken((prev) => prev + 1);
  };

  return (
    <>
      <ApplicationsPage refreshToken={refreshToken} />
      <RecentActivityWidget onRefreshApplications={handleGlobalRefresh} />
    </>
  );
}

export default App;