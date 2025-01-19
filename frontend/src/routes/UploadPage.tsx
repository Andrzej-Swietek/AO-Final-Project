import React, { useState } from "react";

export const UploadPage = () => {
  const [status, setStatus] = useState("Idle");
  const [contentImage, setContentImage] = useState<File | null>(null);
  const [contentImageUrl, setContentImageUrl] = useState<string | null>(null);
  const [resultImages, setResultImages] = useState<string[]>([]);
  const PUBLIC_API_URL = "http://localhost:5000";

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setContentImage(file);
      setContentImageUrl(URL.createObjectURL(file));
    }
  };

  const uploadImage = async () => {
    if (!contentImage) {
      alert("Please upload an image.");
      return;
    }

    const formData = new FormData();
    formData.append("image", contentImage);

    setStatus("Uploading...");
    try {
      const response = await fetch(`${PUBLIC_API_URL}/api/process`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (response.ok) {
        setStatus("Processing...");
        const { task_id } = data;

        // Polling status
        const interval = setInterval(async () => {
          const statusResponse = await fetch(`${PUBLIC_API_URL}/api/status/${task_id}`);
          const statusData = await statusResponse.json();

          if (statusData.status === "Completed") {
            setStatus("Completed");
            setResultImages(statusData.results); 
            clearInterval(interval);
          } else if (statusData.status === "Failed") {
            setStatus("Failed");
            clearInterval(interval);
          }
        }, 2000);
      } else {
        setStatus("Failed");
        console.error(data.error);
      }
    } catch (error) {
      setStatus("Failed");
      console.error("Error uploading the image:", error);
    }
  };

  return (
    <section className="w-full h-full py-12 md:py-24 lg:py-32 bg-muted flex justify-center items-center">
      <div className="container px-4 md:px-6 grid gap-6 w-full h-[90vh]">
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="space-y-2 mb-16">
            <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none">
              Image Segmentation
            </h1>
            <p className="max-w-[900px] text-muted-foreground md:text-xl">
              Upload an image to segment and colorize it based on detected regions.
            </p>
            <p className="max-w-[900px] text-muted-foreground md:text-xl font-bold">Status: {status}</p>
          </div>
          <div className="grid grid-cols-2 gap-4 w-full max-w-4xl">
            <div className="flex flex-col col-span-2 items-center justify-center border-2 border-dashed border-black rounded-lg p-24 space-y-4">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="w-8 h-8 text-muted-foreground"
              >
                <rect width="18" height="18" x="3" y="3" rx="2" ry="2"></rect>
                <circle cx="9" cy="9" r="2"></circle>
                <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"></path>
              </svg>
              <p className="text-sm text-muted-foreground mb-8">Upload Image</p>
              <input
                className="flex h-10 mt-4 font-semibold rounded-md border border-input bg-transparent px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 w-full"
                placeholder="Upload image"
                accept="image/png, image/jpeg"
                type="file"
                onChange={handleFileChange}
              />
            </div>
            {contentImageUrl && (
              <div className="flex flex-col items-center justify-center gap-4 mt-8 col-span-2">
                <p className="text-muted-foreground md:text-xl">Image preview:</p>
                <img className="w-[300px] h-[300px] object-cover rounded-md" src={contentImageUrl} alt="Preview" />
              </div>
            )}
          </div>
          <button
            className="inline-flex text-xl items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-32 py-2 mt-16"
            type="button"
            onClick={uploadImage}
          >
            Process Image
          </button>
        </div>
        <div className="mt-8">
          {resultImages.length > 0 && (
            <>
              <h2 className="text-2xl font-bold mt-4">Results</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {resultImages.map((image, idx) => (
                  <img key={idx} src={image} alt="Segmented and Colorized" className="w-full h-auto" />
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  );
};

