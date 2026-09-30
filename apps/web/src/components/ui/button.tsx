import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  icon?: ReactNode;
};

export function Button({ children, icon, className = "", type = "button", ...props }: ButtonProps) {
  return (
    <button className={`primary-action ${className}`} type={type} {...props}>
      {icon}
      <span>{children}</span>
    </button>
  );
}
