import React, { useState } from "react";
import {useToast} from "@/hooks/use-toast.ts";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

type OperationStatus =
    'Finished'
    | 'Idle'
    | 'Uploading...'
    | 'Failed'
    | 'Processing...';

export const UploadPage = () => {
  const [status, setStatus] = useState<OperationStatus>("Idle");
  const [contentImage, setContentImage] = useState<File | null>(null);
  const [contentImageUrl, setContentImageUrl] = useState<string | null>(null);
  const [resultImages, setResultImages] = useState<string[]>([]);
  const [taskId, setTaskId] = useState<string>("");
  const [colorCount, setColorCount] = useState<string | null>(null);
  const { toast } = useToast()

  const PUBLIC_API_URL = "";
  // const PUBLIC_API_URL =  import.meta.env.VITE_API_URL ?? "";

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setContentImage(file);
      setContentImageUrl(URL.createObjectURL(file));
    }
  };

  const download = async () => {
    const response = await fetch(`${PUBLIC_API_URL}/api/download/${taskId}`);


    if (!response.ok) {
      console.error('Error downloading file:', response.statusText);
      return;
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'result.jpg';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  const uploadImage = async () => {
    if (!contentImage) {
      // alert("Please upload an image.");
      toast({
        title: "Upload Error",
        description: "Please provide an image"
      })
      return;
    }

    if (!colorCount || (parseInt(colorCount) < 1 || parseInt(colorCount) > 33)) {
      toast({
        title: "Invalid Input",
        description: "Please select a color count between 2 and 32"
      });
      return;
    }

    const formData = new FormData();
    formData.append("image", contentImage);
    formData.append("color_count", colorCount?.toString());

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
        setTaskId(task_id);
        // Polling status
        const interval = setInterval(async () => {
          const statusResponse = await fetch(`${PUBLIC_API_URL}/api/task_status/${task_id}`);
          const statusData = await statusResponse.json();

          if (statusData.status === "Finished") {
            setStatus("Finished");
            setResultImages([]);
            clearInterval(interval);
            toast({
              title: "Processing Successful",
              description: "You can now download the images",
            })
          } else if (statusData.status === "Failed") {
            setStatus("Failed");
            clearInterval(interval);
            toast({
              title: "Processing Error",
              description: "Please try again later",
            })
          }
        }, 2000);
      } else {
        setStatus("Failed");
        toast({
          title: "Processing Error",
          description: "Please try again later",
        })
        console.error(data.error);
      }
    } catch (error) {
      setStatus("Failed");
      toast({
        title: "Processing Error",
        description: "Please try again later",
      })
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
          {
            status != 'Finished' ? (
                <>
                  <div className="grid grid-cols-2 gap-4 w-full max-w-4xl">
                    <div
                        className="flex flex-col col-span-2 items-center justify-center border-2 border-dashed border-black rounded-lg p-24 space-y-4">
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
                          <img className="w-[300px] h-[300px] object-cover rounded-md" src={contentImageUrl}
                               alt="Preview"/>
                        </div>
                    )}
                  </div>
                  <div className="flex flex-col items-start w-[280px] mt-4">
                    <label htmlFor="colorCount" className="text-sm font-medium text-muted-foreground mb-2">
                      Select Color Count
                    </label>
                     <Select
                         onValueChange={(value) => setColorCount(value)}
                     >
                      <SelectTrigger className="w-[280px]">
                        <SelectValue
                            placeholder="Select number of colors"
                            // value={colorCount}
                        />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectGroup>
                          <SelectLabel>Color count</SelectLabel>
                          {
                            [2, 3, 4, 5, 6, 8, 10, 12, 16, 24, 32].map(num=>
                                <SelectItem key={num} value={`${num}`}>{num}</SelectItem>
                            )
                          }
                        </SelectGroup>
                      </SelectContent>
                    </Select>
                  </div>
                </>
            ) : (
                <>
                  <div className="grid grid-cols-2 gap-4 w-full max-w-4xl">
                    <img src={`http://localhost:5000/api/view/${taskId}`} alt={"Kolorowanka"}/>
                    <img src={`http://localhost:5000/api/view/${taskId}/final-image`} alt={"Wypełniona"}/>
                  </div>
                </>
            )
          }


          {
            status == 'Finished' ? (
                <>
                  <button
                      className="inline-flex text-xl items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-32 py-2 mt-16"
                      type="button"
                      onClick={() => download()}
                  >
                    Download
                  </button>
                  <button
                      className="inline-flex text-xl items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-32 py-2 mt-16"
                      type="button"
                      onClick={() => window.location.reload()}
                  >
                    Reset
                  </button>
                </>
            ) : (
                <button
                    className="inline-flex text-xl items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-32 py-2 mt-16"
                    type="button"
                    onClick={uploadImage}
                >
                  Process Image
                </button>
            )
          }
        </div>

        <div className="mt-8">
          {resultImages.length > 0 && (
              <>
                <h2 className="text-2xl font-bold mt-4">Results</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                  {resultImages.map((image, idx) => (
                      <img key={idx} src={image} alt="Segmented and Colorized" className="w-full h-auto"/>
                  ))}
                </div>
              </>
          )}
        </div>
      </div>
    </section>
  );
};

