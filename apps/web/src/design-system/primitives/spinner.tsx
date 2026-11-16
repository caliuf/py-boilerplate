import { Loader2Icon } from "lucide-react";
import { cn } from "@/design-system/lib/utils";

type SpinnerProps = React.ComponentProps<"output"> & {
  readonly label?: string;
};

/** Standalone loading indicator with an accessible status label. */
function Spinner({ className, label = "Loading", ...props }: SpinnerProps) {
  return (
    <output
      data-slot="spinner"
      aria-label={label}
      className={cn("inline-flex items-center justify-center", className)}
      {...props}
    >
      <Loader2Icon aria-hidden="true" className="size-4 animate-spin" />
    </output>
  );
}

export { Spinner };
