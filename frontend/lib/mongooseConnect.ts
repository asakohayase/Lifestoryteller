import mongoose, { ConnectOptions } from "mongoose";

const connection: {
  [key: string]: any;
} = {};

async function dbConnect() {
  // Check if we have a connection to the database or if it's currently connecting or disconnecting
  if (connection.isConnected) {
    return;
  }

  const uri = process.env.MONGODB_URI || "";

  // Using new db connection config
  const db = await mongoose.connect(
    process.env.MONGODB_URI || "",
    {} as ConnectOptions
  );

  connection.isConnected = db.connections[0].readyState;
}

export default dbConnect;
