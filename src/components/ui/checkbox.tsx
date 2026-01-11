import * as React from "react"

import { cn } from "@/lib/utils"

function Checkbox({ className, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type="checkbox"
      data-slot="checkbox"
      className={cn(
        "border-input h-4 w-4 shrink-0 rounded border bg-transparent shadow-xs transition-colors outline-none disabled:cursor-not-allowed disabled:opacity-50",
        "focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]",
        "checked:bg-primary checked:border-primary checked:text-primary-foreground",
        className
      )}
      {...props}
    />
  )
}

export { Checkbox }
