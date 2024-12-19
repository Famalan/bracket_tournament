import { Button } from "./ui/button";

export const TournamentTypes = () => {
    return (
        <div className="py-24">
            <div className="container">
                <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
                    Tournament Formats
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {[
                        {
                            title: "Single Elimination",
                            description:
                                "Classic bracket-style tournament with direct elimination",
                            features: [
                                "Quick progression",
                                "Clear winners",
                                "Ideal for large groups",
                            ],
                        },
                        {
                            title: "Double Elimination",
                            description:
                                "Two chances to advance with winners and losers brackets",
                            features: [
                                "Second chances",
                                "More matches",
                                "Fair competition",
                            ],
                        },
                        {
                            title: "Round Robin",
                            description:
                                "Everyone plays against everyone for maximum fairness",
                            features: [
                                "Equal opportunities",
                                "Complete rankings",
                                "Best for small groups",
                            ],
                        },
                    ].map((type, index) => (
                        <div
                            key={index}
                            className="p-6 rounded-lg bg-secondary/20 border border-secondary hover:border-primary/50 transition-colors duration-300"
                        >
                            <h3 className="text-xl font-semibold mb-4">
                                {type.title}
                            </h3>
                            <p className="text-muted-foreground mb-6">
                                {type.description}
                            </p>
                            <ul className="space-y-2 mb-6">
                                {type.features.map((feature, fIndex) => (
                                    <li
                                        key={fIndex}
                                        className="flex items-center gap-2"
                                    >
                                        <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                                        {feature}
                                    </li>
                                ))}
                            </ul>
                            <Button variant="secondary" className="w-full">
                                Learn More
                            </Button>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};
