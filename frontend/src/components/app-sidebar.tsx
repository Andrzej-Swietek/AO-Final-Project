import {
    Sidebar,
    SidebarContent,
    SidebarGroup,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
  } from "@/components/ui/sidebar"
import { Home, Info, Images } from "lucide-react"


const items = [
    {
      title: "Home",
      url: "/",
      icon: Home,
    },
    {
        title: "Action",
        url: "/upload",
        icon: Images,
      },
    {
      title: "Info",
      url: "/info",
      icon: Info,
    },
  ]

export const AppSidebar = () => {
    return (
        <Sidebar>
        <SidebarContent>
          <SidebarGroup>
            <div className="h-[30vh]"></div>
            <SidebarGroupLabel className="text-2xl font-black">Application</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {items.map((item) => (
                  <SidebarMenuItem className="text-2xl font-thin mt-4" key={item.title}>
                    <SidebarMenuButton asChild>
                      <a className="py-4 px-4 lg:px-8 h-[70px]" href={item.url}>
                        <item.icon className="text-2xl font-black" />
                        <span className="text-xl font-thin">{item.title}</span>
                      </a>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
      </Sidebar>
  
    )
}