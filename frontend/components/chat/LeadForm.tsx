"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Loader2, CheckCircle } from "lucide-react";

const leadSchema = z.object({
  fullName: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Please enter a valid email"),
  phone: z.string().regex(/^(\+966|966|0)?5\d{8}$/, "Please enter a valid Saudi phone number"),
  company: z.string().optional(),
  inquiryType: z.string().optional(),
});

type LeadFormData = z.infer<typeof leadSchema>;

interface LeadFormProps {
  onSubmit: (data: LeadFormData) => Promise<void>;
  isLoading?: boolean;
}

export function LeadForm({ onSubmit, isLoading }: LeadFormProps) {
  const [isSuccess, setIsSuccess] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LeadFormData>({
    resolver: zodResolver(leadSchema),
  });

  const handleFormSubmit = async (data: LeadFormData) => {
    await onSubmit(data);
    setIsSuccess(true);
  };

  if (isSuccess) {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardContent className="pt-6 text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">Thank You!</h3>
          <p className="text-muted-foreground">
            Your information has been submitted successfully. Starting conversation...
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="text-center">
        <div className="w-16 h-16 bg-gradient-to-br from-[#E30613] to-[#C00510] rounded-2xl mx-auto mb-4 flex items-center justify-center">
          <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
        </div>
        <CardTitle className="text-2xl">Get Started</CardTitle>
        <CardDescription>
          Please provide your details so we can assist you better.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="fullName">
              Full Name <span className="text-[#E30613]">*</span>
            </Label>
            <Input
              id="fullName"
              placeholder="Enter your full name"
              {...register("fullName")}
              className={errors.fullName ? "border-red-500" : ""}
            />
            {errors.fullName && (
              <p className="text-sm text-red-500">{errors.fullName.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">
              Email Address <span className="text-[#E30613]">*</span>
            </Label>
            <Input
              id="email"
              type="email"
              placeholder="your@email.com"
              {...register("email")}
              className={errors.email ? "border-red-500" : ""}
            />
            {errors.email && (
              <p className="text-sm text-red-500">{errors.email.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="phone">
              Phone Number <span className="text-[#E30613]">*</span>
            </Label>
            <Input
              id="phone"
              placeholder="+966 5xxxxxxxx"
              {...register("phone")}
              className={errors.phone ? "border-red-500" : ""}
            />
            {errors.phone && (
              <p className="text-sm text-red-500">{errors.phone.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="company">Company (Optional)</Label>
            <Input
              id="company"
              placeholder="Your company name"
              {...register("company")}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="inquiryType">Inquiry Type</Label>
            <select
              id="inquiryType"
              {...register("inquiryType")}
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
            >
              <option value="">Select inquiry type</option>
              <option value="Product Information">Product Information</option>
              <option value="Pricing Quote">Pricing Quote</option>
              <option value="Technical Support">Technical Support</option>
              <option value="Partnership">Partnership</option>
              <option value="Careers">Careers</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <Button
            type="submit"
            className="w-full bg-gradient-to-r from-[#E30613] to-[#C00510] hover:opacity-90"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Submitting...
              </>
            ) : (
              "Start Conversation"
            )}
          </Button>

          <p className="text-xs text-center text-muted-foreground mt-4">
            By submitting, you agree to our privacy policy. Your information is secure.
          </p>
        </form>
      </CardContent>
    </Card>
  );
}
