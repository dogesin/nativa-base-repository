"use client"

import * as React from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"

export function TextField({
  id,
  label,
  error,
  className,
  ...props
}: React.ComponentProps<typeof Input> & {
  label?: string
  error?: string
}) {
  return (
    <div className={cn("space-y-2", className)}>
      {label && <Label htmlFor={id}>{label}</Label>}
      <Input id={id} aria-invalid={!!error} {...props} />
      {error && (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}
