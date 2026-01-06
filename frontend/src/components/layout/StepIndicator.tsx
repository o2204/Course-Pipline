import { motion } from "framer-motion";
import { Check } from "lucide-react";
import { useLocation, Link } from "react-router-dom";

const steps = [
  { path: "/", label: "Upload", step: 1 },
  { path: "/images", label: "Storyboard", step: 2 },
  { path: "/frames", label: "Selection", step: 3 },
];

export function StepIndicator() {
  const location = useLocation();
  const currentStep = steps.findIndex((s) => s.path === location.pathname) + 1;

  return (
    <div className="flex items-center justify-center gap-2 mb-10">
      {steps.map((step, index) => {
        const isCompleted = currentStep > step.step;
        const isCurrent = currentStep === step.step;

        return (
          <div key={step.path} className="flex items-center">
            <Link
              to={step.path}
              className="flex items-center gap-2 group"
            >
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: index * 0.1 }}
                className={`
                  relative w-10 h-10 rounded-full flex items-center justify-center font-medium text-sm
                  transition-all duration-300
                  ${isCompleted 
                    ? "bg-primary text-primary-foreground" 
                    : isCurrent 
                      ? "bg-primary/20 text-primary border-2 border-primary" 
                      : "bg-muted text-muted-foreground group-hover:bg-muted/80"
                  }
                `}
              >
                {isCompleted ? (
                  <Check className="w-5 h-5" />
                ) : (
                  step.step
                )}
                {isCurrent && (
                  <motion.div
                    layoutId="activeStep"
                    className="absolute inset-0 rounded-full border-2 border-primary"
                    initial={false}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
              </motion.div>
              <span className={`
                text-sm font-medium hidden sm:block transition-colors
                ${isCurrent ? "text-foreground" : "text-muted-foreground group-hover:text-foreground"}
              `}>
                {step.label}
              </span>
            </Link>
            {index < steps.length - 1 && (
              <div className={`
                w-12 h-0.5 mx-2 rounded-full transition-colors
                ${currentStep > step.step ? "bg-primary" : "bg-border"}
              `} />
            )}
          </div>
        );
      })}
    </div>
  );
}
