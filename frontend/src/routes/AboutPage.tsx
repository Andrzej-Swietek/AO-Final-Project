import { FC } from "react"
import { User } from "lucide-react"
import { cn } from "@/lib/utils";



export const AboutPage: FC = () => {
    return (
      <>
        <section className="w-full py-12 md:py-24 lg:py-32 flex justify-center">
          <div className="container px-4 md:px-6">
            {/* Mission Section */}
            <div className="flex flex-col items-center justify-center space-y-4 text-center mb-16">
              <div className="space-y-2">
                <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">Our Project</h2>
                <p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                  Our project focuses on advancing image analysis by developing methods for color segmentation and automated colorization. By combining modern machine learning techniques with image processing, we aim to provide tools that aid in academic, artistic, and industrial applications.
                </p>
              </div>
            </div>
  
            {/* Team Section */}
            <div className="mx-auto grid max-w-5xl items-center gap-6 py-12 lg:grid-cols-2 lg:gap-12">
              <img
                src="/team.png"
                width="550"
                height="310"
                alt="Project Team"
                className="mx-auto aspect-video overflow-hidden rounded-xl object-cover object-center sm:w-full lg:order-last"
              />
              <div className="flex flex-col justify-center space-y-4">
                <div className="space-y-2">
                  <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl mb-4">Meet the Team</h2>
                  <p className="max-w-[600px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                    Our interdisciplinary team consists of students specializing in machine learning, computer vision, and software engineering. Together, we aim to deliver a meaningful contribution to the field of image analysis while gaining practical experience through collaboration.
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <PersonCard name="Aleksandra Samborek" role="" />
                  <div className="col-span-2 grid grid-cols-2 gap-4">
                    <PersonCard className="col-span-1" name="Andrzej Świętek" role="" />
                    <PersonCard className="col-span-1" name="Krzystof Konieczny" role="" />
                  </div>
                  <PersonCard name="Marcin Knapczyk" role="" />
                </div>
              </div>
            </div>
  
            {/* Technologies Section */}
            <div className="flex flex-col items-center justify-center space-y-4 text-center mt-16">
              <div className="space-y-2">
                <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">Technologies We Use</h2>
                <p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                  This project is powered by modern technologies such as Python for backend image processing, Flask for API development, React with TypeScript for the user interface, and machine learning frameworks for segmentation and colorization.
                </p>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-8">
                <TechnologyCard name="Python" />
                <TechnologyCard name="Flask" />
                <TechnologyCard name="React" />
                <TechnologyCard name="TypeScript" />
                <TechnologyCard name="OpenCV" />
                <TechnologyCard name="Docker" />

              </div>
            </div>
          </div>
        </section>
      </>
    );
  };
  
  const PersonCard: FC<{ name: string; role: string, className?: string }> = ({ name, role, className= "" }) => (
    <div className={cn("flex flex-col items-center justify-center space-y-2 col-span-2", className)}>
      <span className="relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full">
        <User className="aspect-square h-full w-full" />
      </span>
      <p className="text-sm font-medium">{name}</p>
      <p className="text-sm text-muted-foreground">{role}</p>
    </div>
  );
  
  const TechnologyCard: FC<{ name: string }> = ({ name }) => (
    <div className="flex items-center justify-center p-4 border rounded-md shadow-sm bg-muted">
      <p className="text-sm font-medium">{name}</p>
    </div>
  );