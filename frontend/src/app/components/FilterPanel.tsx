import { ChevronDown, Filter as FilterIcon, X } from "lucide-react";
import { Button } from "./ui/button";
import { Checkbox } from "./ui/checkbox";
import { Slider } from "./ui/slider";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "./ui/collapsible";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { useState } from "react";
import { useSearchParams } from "react-router";

interface FilterPanelProps {
  onClose?: () => void;
  isMobile?: boolean;
}

const mainCategories = [
  { id: "clothing", label: "Clothing" },
  { id: "cosmetics", label: "Cosmetics" },
];

export function FilterPanel({ onClose, isMobile = false }: FilterPanelProps) {
  const [searchParams, setSearchParams] = useSearchParams();
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({
    categories: true,
    size: true,
    color: true,
    skin_type: true,
    finish: true,
    ingredients: true,
  });

  const category = searchParams.get("category");
  const sizeParam = searchParams.get("size");
  const colorParam = searchParams.get("color");
  const skinTypeParam = searchParams.get("skin_type");
  const finishParam = searchParams.get("finish");
  const isVegan = searchParams.get("is_vegan") === "true";
  const isCrueltyFree = searchParams.get("is_cruelty_free") === "true";

  const toggleSection = (section: string) => {
    setOpenSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const updateParam = (key: string, value: string | null) => {
    const newParams = new URLSearchParams(searchParams);
    if (value) {
      newParams.set(key, value);
    } else {
      newParams.delete(key);
    }
    setSearchParams(newParams);
  };

  const clearAllFilters = () => {
    setSearchParams(new URLSearchParams());
  };

  // Check how many filters are active
  const filterCount = Array.from(searchParams.keys()).filter(k => k !== 'q').length;

  return (
    <Card className={`h-fit sticky top-20 ${isMobile ? 'w-full' : 'w-80'}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <FilterIcon className="h-4 w-4" />
            Filters
            {filterCount > 0 && (
              <span className="bg-primary text-primary-foreground text-xs px-2 py-1 rounded-full">
                {filterCount}
              </span>
            )}
          </CardTitle>
          <div className="flex gap-1">
            {filterCount > 0 && (
              <Button variant="ghost" size="sm" onClick={clearAllFilters}>
                Clear
              </Button>
            )}
            {isMobile && (
              <Button variant="ghost" size="sm" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Categories */}
        <Collapsible open={openSections.categories} onOpenChange={() => toggleSection('categories')}>
          <CollapsibleTrigger asChild>
            <Button variant="ghost" className="w-full justify-between p-0 h-auto">
              <span>Categories</span>
              <ChevronDown className={`h-4 w-4 transition-transform ${openSections.categories ? 'rotate-180' : ''}`} />
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent className="mt-3 space-y-3">
            {mainCategories.map((c) => (
              <div key={c.id} className="flex items-center space-x-2">
                <Checkbox
                  id={`cat-${c.id}`}
                  checked={category === c.id}
                  onCheckedChange={(checked) => updateParam("category", checked ? c.id : null)}
                />
                <label htmlFor={`cat-${c.id}`} className="text-sm cursor-pointer">{c.label}</label>
              </div>
            ))}
          </CollapsibleContent>
        </Collapsible>

        {/* Clothing Filters */}
        {(!category || category === "clothing") && (
          <>
            <Collapsible open={openSections.size} onOpenChange={() => toggleSection('size')}>
              <CollapsibleTrigger asChild>
                <Button variant="ghost" className="w-full justify-between p-0 h-auto">
                  <span>Size</span>
                  <ChevronDown className={`h-4 w-4 transition-transform ${openSections.size ? 'rotate-180' : ''}`} />
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="mt-3 flex flex-wrap gap-2">
                {['S', 'M', 'L', 'XL'].map((s) => (
                  <Button 
                    key={s} 
                    variant={sizeParam === s ? 'default' : 'outline'} 
                    size="sm"
                    onClick={() => updateParam("size", sizeParam === s ? null : s)}
                  >
                    {s}
                  </Button>
                ))}
              </CollapsibleContent>
            </Collapsible>

            <Collapsible open={openSections.color} onOpenChange={() => toggleSection('color')}>
              <CollapsibleTrigger asChild>
                <Button variant="ghost" className="w-full justify-between p-0 h-auto">
                  <span>Color</span>
                  <ChevronDown className={`h-4 w-4 transition-transform ${openSections.color ? 'rotate-180' : ''}`} />
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="mt-3 flex flex-wrap gap-2">
                {['Black', 'White', 'Red', 'Blue'].map((c) => (
                  <Button 
                    key={c} 
                    variant={colorParam === c ? 'default' : 'outline'} 
                    size="sm"
                    onClick={() => updateParam("color", colorParam === c ? null : c)}
                  >
                    {c}
                  </Button>
                ))}
              </CollapsibleContent>
            </Collapsible>
          </>
        )}

        {/* Cosmetics Filters */}
        {(!category || category === "cosmetics") && (
          <>
            <Collapsible open={openSections.skin_type} onOpenChange={() => toggleSection('skin_type')}>
              <CollapsibleTrigger asChild>
                <Button variant="ghost" className="w-full justify-between p-0 h-auto">
                  <span>Skin Type</span>
                  <ChevronDown className={`h-4 w-4 transition-transform ${openSections.skin_type ? 'rotate-180' : ''}`} />
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="mt-3 space-y-3">
                {['Oily', 'Dry', 'Combination', 'Sensitive'].map((st) => (
                  <div key={st} className="flex items-center space-x-2">
                    <Checkbox
                      id={`st-${st}`}
                      checked={skinTypeParam === st}
                      onCheckedChange={(checked) => updateParam("skin_type", checked ? st : null)}
                    />
                    <label htmlFor={`st-${st}`} className="text-sm cursor-pointer">{st}</label>
                  </div>
                ))}
              </CollapsibleContent>
            </Collapsible>

            <Collapsible open={openSections.finish} onOpenChange={() => toggleSection('finish')}>
              <CollapsibleTrigger asChild>
                <Button variant="ghost" className="w-full justify-between p-0 h-auto">
                  <span>Finish</span>
                  <ChevronDown className={`h-4 w-4 transition-transform ${openSections.finish ? 'rotate-180' : ''}`} />
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="mt-3 space-y-3">
                {['Matte', 'Dewy', 'Glossy'].map((f) => (
                  <div key={f} className="flex items-center space-x-2">
                    <Checkbox
                      id={`f-${f}`}
                      checked={finishParam === f}
                      onCheckedChange={(checked) => updateParam("finish", checked ? f : null)}
                    />
                    <label htmlFor={`f-${f}`} className="text-sm cursor-pointer">{f}</label>
                  </div>
                ))}
              </CollapsibleContent>
            </Collapsible>

            <Collapsible open={openSections.ingredients} onOpenChange={() => toggleSection('ingredients')}>
              <CollapsibleTrigger asChild>
                <Button variant="ghost" className="w-full justify-between p-0 h-auto">
                  <span>Ingredients</span>
                  <ChevronDown className={`h-4 w-4 transition-transform ${openSections.ingredients ? 'rotate-180' : ''}`} />
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="mt-3 space-y-3">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="vegan"
                    checked={isVegan}
                    onCheckedChange={(checked) => updateParam("is_vegan", checked ? "true" : null)}
                  />
                  <label htmlFor="vegan" className="text-sm cursor-pointer">Vegan</label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="cruelty_free"
                    checked={isCrueltyFree}
                    onCheckedChange={(checked) => updateParam("is_cruelty_free", checked ? "true" : null)}
                  />
                  <label htmlFor="cruelty_free" className="text-sm cursor-pointer">Cruelty-Free</label>
                </div>
              </CollapsibleContent>
            </Collapsible>
          </>
        )}
      </CardContent>
    </Card>
  );
}