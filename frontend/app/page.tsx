"use client";

import { testDbConnection } from "@/actions/test.actions";
import { useState } from "react";

type ConnectionResult =
  | { success: true; message: string; data: any }
  | { success: false; message: string; error: string };

export default function Home() {
  const [result, setResult] = useState<ConnectionResult | null>(null);

  const handleTestConnection = async () => {
    const connectionResult = await testDbConnection();
    setResult(connectionResult);
  };

  return (
    <div>
      <button onClick={handleTestConnection}>Test Database Connection</button>
      {result && (
        <div>
          <p>Connection success: {result.success ? "Yes" : "No"}</p>
          <p>Message: {result.message}</p>
          {!result.success && <p>Error: {result.error}</p>}
          {result.success && <p>Data: {JSON.stringify(result.data)}</p>}
        </div>
      )}
    </div>
  );
}
