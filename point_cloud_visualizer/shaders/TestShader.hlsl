struct VSInput
{
    float3 position : POSITION;
    float2 textureCoord : TEXTURECOORD;
};

struct VSOutput
{
    float4 position : SV_Position;
    float2 textureCoord : TEX_COORD;
};

cbuffer sceneBuffer : register(b0)
{
    row_major matrix modelMatrix;
    row_major matrix viewMatrix;
    row_major matrix viewProjectionMatrix;
    float layerCount;
}

Texture2D<float> depthTexture : register(t0);
SamplerState smp : register(s0); 

VSOutput VsMain(VSInput input, uint instanceID : SV_InstanceID)
{
    const int IMG_WIDTH = 132;
    const int IMG_HEIGHT = 60;

    int width;
    int height;
    depthTexture.GetDimensions(width, height);

    const float2 offset = 1.0f / float2(width, height);

    float2 texCoords = float2(instanceID / IMG_HEIGHT, (instanceID % IMG_HEIGHT)) / float2((float)IMG_WIDTH, (float)IMG_HEIGHT);
    texCoords.x = 1.0f - texCoords.x;

    const float zCoord = 25.0f * instanceID / IMG_WIDTH;

    VSOutput output;
    output.position = mul(mul(float4(input.position.xyz + float3(texCoords * float2(IMG_WIDTH, IMG_HEIGHT), 0.0f), 1.0f), modelMatrix), viewProjectionMatrix);
    output.textureCoord = texCoords;

    return output;
}

Texture2D<float4> tex : register(t0);

struct PSOutput
{
    float4 color : SV_Target;
};

PSOutput PsMain(VSOutput input)
{
    PSOutput output;
    output.color = tex.Sample(smp, input.textureCoord);
   
    return output;
}