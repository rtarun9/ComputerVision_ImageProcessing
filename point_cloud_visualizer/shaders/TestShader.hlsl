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
    uint imageSelect;
}

Texture2D<float4> depthTexture : register(t0);
SamplerState smp : register(s0); 

VSOutput VsMain(VSInput input, uint instanceID : SV_InstanceID)
{
    int width;
    int height;
    depthTexture.GetDimensions(width, height);

    const int IMG_WIDTH = width;
    const int IMG_HEIGHT = height;

    const float2 offset = 1.0f / float2(width, height);

    float2 texCoords = float2(instanceID / IMG_HEIGHT, (instanceID % IMG_HEIGHT)) / float2((float)IMG_WIDTH, (float)IMG_HEIGHT);
    texCoords.y = 1.0f - texCoords.y;

    const float3 depthTextureValue = depthTexture.SampleLevel(smp, texCoords, 0u).xyz;

    const float zCoord = -1.0f * (depthTextureValue.x + depthTextureValue.y + depthTextureValue.z) * layerCount;

    VSOutput output;
    output.position = mul(mul(float4(input.position.xyz + float3(texCoords * float2(IMG_WIDTH, -IMG_HEIGHT), (zCoord)), 1.0f), modelMatrix), viewProjectionMatrix);
    output.textureCoord = texCoords;

    return output;
}

Texture2D<float4> tex : register(t1);
Texture2D<float4> disparityMap : register(t2);

struct PSOutput
{
    float4 color : SV_Target;
};

PSOutput PsMain(VSOutput input)
{
    PSOutput output;
    
    if (imageSelect == 0u)
    {
        output.color = tex.Sample(smp, input.textureCoord);
    }
    else if (imageSelect == 1u)
    {
        output.color = disparityMap.Sample(smp, input.textureCoord);
    }
    else if (imageSelect == 2u)
    {
        output.color = depthTexture.Sample(smp, input.textureCoord).ggga;
    }
   
    return output;
}