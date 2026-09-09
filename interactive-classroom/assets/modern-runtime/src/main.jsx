import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";

function readCourse(){
 const node=document.getElementById("course-data");
 if(!node) throw new Error("Missing #course-data");
 return JSON.parse(node.textContent || "{}");
}

const course=readCourse();
createRoot(document.getElementById("root")).render(
 <React.StrictMode>
 <App course={course} />
 </React.StrictMode>
);
