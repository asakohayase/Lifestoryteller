"use server";

import dbConnect from "../lib/mongooseConnect";

type ConnectionResult =
  | { success: true; message: string; data: any }
  | { success: false; message: string; error: string };

export async function testDbConnection(): Promise<ConnectionResult> {
  try {
    await dbConnect();
    const mongoose = await import("mongoose");
    const db = mongoose.connection;
    const result = await db.collection("test").findOne({});
    return {
      success: true,
      message: "Database connection successful",
      data: result,
    };
  } catch (error) {
    console.error("Database connection failed:", error);
    return {
      success: false,
      message: "Database connection failed",
      error:
        error instanceof Error ? error.stack || error.message : String(error),
    };
  }
}
