#version 430 
#define STEP_SIZE_X 64

const int stepSize = int(STEP_SIZE_X);
layout(local_size_x=STEP_SIZE_X) in;

const int TEX_SIZE = 512;
const int TILE_SIZE = 32;
const int TILE_COUNT = int(TEX_SIZE / TILE_SIZE);
const int TILE_GCOUNT = (TEX_SIZE*TEX_SIZE) / (TILE_SIZE * TILE_SIZE);


layout(binding=1) buffer tex
{ 
    vec4 Texture[];
};

layout(binding=2) buffer ic
{ 
    vec4 in_coords[];
};

layout(binding=3) buffer oc
{ 
    vec4 data[];
};

layout(binding=4) buffer co
{ 
    vec4 color;
};

layout(binding=5) buffer ui
{ 
    //vec4 use_image;
    vec4 params; // ImageSizeX, ImageSizeY, UseImageFlag
};


int FractToPixelID(float u, float v, int texSize)
{   
    int _idx = ((int(v*texSize)) * texSize) + (int(u*texSize));
    
    return _idx;
}

vec2 PixelIDtoFract(int pixelIndex, int TEX_SIZE)
{
    int pxX = pixelIndex % TEX_SIZE;
    int pxY = int((pixelIndex - pxX) / TEX_SIZE);
    
    vec2 uv = vec2(pxX, pxY) / TEX_SIZE;
    
    return uv;
}

ivec2 IndexToTileXY(int tileIndex, int TILE_COUNT)
{
    int tileX = (tileIndex % TILE_COUNT);
    int tileY = int((tileIndex-tileX) / TILE_COUNT) + 1;
    
    return ivec2(tileX, tileY);
}

ivec2 TileToPixel(int tileIndex, int TILE_COUNT, int TILE_SIZE)
{
    ivec2 tileXY = IndexToTileXY(tileIndex+1, TILE_COUNT);
    ivec2 pxXY = (tileXY + ivec2(1,0)) * TILE_SIZE;
    
    return pxXY;
}

vec3 RGB2HSV(vec3 c)
{
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

vec2 TexcoordFromPalette(vec3 old_color)
{
    vec3 hsv = RGB2HSV(old_color);

    ivec2 tileSV = ivec2(int((1-hsv.y) * TILE_SIZE)-1, int((1-hsv.z) * (TILE_SIZE-1)));
    ivec2 hueTile = TileToPixel(int(hsv.x * TILE_GCOUNT)-1, TILE_COUNT, TILE_SIZE);
    ivec2 result = ivec2(hueTile.x - tileSV.x, hueTile.y - tileSV.y);
    
    return vec2(result.xy)/TEX_SIZE;
}

void main() 
{
    const int glob = int(gl_GlobalInvocationID);
    
    vec4 pixel_color;

    if (params.z < 0.5)
    {
        pixel_color = vec4(color.rgb, 1);
    }
    else
    {
        int idx = FractToPixelID(in_coords[glob].x, in_coords[glob].y, int(params.x));
        pixel_color = Texture[idx] * vec4(color.rgb, 1);
    }

    vec2 out_texcoord = TexcoordFromPalette(pixel_color.rgb);

    vec2 half_pixel_offset = vec2((float(1)/TEX_SIZE)/2);
    vec3 hsv = RGB2HSV(pixel_color.rgb);
    
    data[glob] = vec4(fract(out_texcoord.xy-half_pixel_offset), pixel_color.r, hsv.x);
}
