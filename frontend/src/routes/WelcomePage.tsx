import React from "react";
import { Button } from "@/components/ui/button";

export const WelcomePage: React.FC = () => {
  return (
    <div className="text-center h-screen flex flex-col justify-center items-center gap-4">
      <h1 className="text-7xl font-black mb-4">Welcome to the Colorization App</h1>
      <p className="text-gray-600 text-3xl font-thin mb-6">
        Upload an image and transform it into a coloring page.
      </p>
      <Button asChild>
        <a href="/upload">Get Started</a>
      </Button>
    </div>
  );
};


