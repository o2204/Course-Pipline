import { motion } from "framer-motion";
import { Moon, Sun, Sparkles } from "lucide-react";
import { useTheme } from "@/lib/theme";
import { Button } from "@/components/ui/button";

export function Header() {
  const { theme, toggleTheme } = useTheme();

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="sticky top-0 left-0 right-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl"
    >
      <div className="container mx-auto px-6 h-16 flex items-center justify-between">
        <motion.div 
          className="flex items-center gap-3"
          whileHover={{ scale: 1.02 }}
          transition={{ type: "spring", stiffness: 400 }}
        >
          <div className="relative">
            <div className="w-9 h-9 rounded-lg bg-gradient-primary flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-primary-foreground" />
            </div>
            <div className="absolute inset-0 rounded-lg bg-gradient-primary opacity-50 blur-lg" />
          </div>
          <span className="font-semibold text-lg tracking-tight">
            Storyboard<span className="gradient-text">AI</span>
          </span>
        </motion.div>

        <Button
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
          className="relative overflow-hidden"
        >
          <motion.div
            initial={false}
            animate={{ 
              rotate: theme === "dark" ? 0 : 180,
              scale: theme === "dark" ? 1 : 0 
            }}
            transition={{ duration: 0.3 }}
            className="absolute"
          >
            <Moon className="h-5 w-5" />
          </motion.div>
          <motion.div
            initial={false}
            animate={{ 
              rotate: theme === "light" ? 0 : -180,
              scale: theme === "light" ? 1 : 0 
            }}
            transition={{ duration: 0.3 }}
            className="absolute"
          >
            <Sun className="h-5 w-5" />
          </motion.div>
        </Button>
      </div>
    </motion.header>
  );
}
