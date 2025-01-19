import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"
import { AboutPage, UploadPage, WelcomePage } from "./routes";
import './App.css'

const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">


      <SidebarProvider>
        <AppSidebar />
        <main className="container mx-auto px-4 py-6">
          <SidebarTrigger />
            <Routes>
              <Route path="/" element={<WelcomePage />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/info" element={<AboutPage />} />
            </Routes>
        </main>
      </SidebarProvider>


      </div>
    </Router>
  );
};

export default App;