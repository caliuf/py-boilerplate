import type { ReactNode } from "react";

type PageProps = {
  readonly title: string;
  readonly description?: string | undefined;
  readonly children: ReactNode;
};

type PageHeaderProps = {
  readonly title: string;
  readonly description?: string | undefined;
};

/** Page header pattern shared by feature screens. */
export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <header className="flex flex-col gap-2">
      <h1 className="font-heading text-2xl font-semibold tracking-tight text-balance sm:text-3xl">
        {title}
      </h1>
      {description === undefined ? null : (
        <p className="max-w-prose text-sm text-muted-foreground text-pretty sm:text-base">
          {description}
        </p>
      )}
    </header>
  );
}

/** Page layout pattern: a single main landmark with a consistent rhythm. */
export function Page({ title, description, children }: PageProps) {
  return (
    <main
      id="main"
      className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-8 px-4 py-10 sm:px-6 lg:py-16"
    >
      <PageHeader title={title} description={description} />
      {children}
    </main>
  );
}
